from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from celery import shared_task
from django.db.models import Max
from django.utils import timezone
from scipy.stats import ks_2samp
from sqlalchemy import text
from sklearn.ensemble import IsolationForest

from .db_utils import ensure_django_alias, get_sqla_engine
from .models import DataSource, DetectorConfig, GenericEvent, ScoredEvent
from .utils_model import load, paths, save
from .vectorize import build_vectorizer

_RETTRAIN_AFTER = timedelta(days=7)
_MAX_SAMPLES = 20_000
_NEW_TREES_EACH_RUN = 25
_MAX_TREES = 400
_DRIFT_PVAL = 1e-3


def _to_aware(ts):
    if isinstance(ts, pd.Timestamp) and ts.tz is None:
        ts = ts.tz_localize(timezone.get_current_timezone())
    elif timezone.is_naive(ts):
        ts = timezone.make_aware(ts, timezone.get_current_timezone())
    return ts.to_pydatetime()


def _series_key(row: pd.Series, series_cols: str) -> str:
    if not series_cols:
        return ""
    cols = [c.strip() for c in series_cols.split(",") if c.strip()]
    return "/".join(str(row[c]) for c in cols)


def _fetch_new_rows(ds: DataSource) -> pd.DataFrame:
    eng = get_sqla_engine(ds)
    last_seen = GenericEvent.objects.filter(datasource_alias=ds.alias).aggregate(
        Max("timestamp")
    ).get("timestamp__max") or datetime(1970, 1, 1)

    q = text(
        f"""
        SELECT *
          FROM ({ds.sql}) AS t
         WHERE {ds.ts_column} > :last
         ORDER BY {ds.ts_column}
        """
    )
    return pd.read_sql(q, eng, params={"last": last_seen})


def _bulk_ingest(ds: DataSource, df: pd.DataFrame) -> None:
    events = [
        GenericEvent(
            datasource_alias=ds.alias,
            timestamp=_to_aware(row[ds.ts_column]),
            series_key=_series_key(row, ds.series_cols),
            payload={k: _clean(v) for k, v in row.items()},
        )
        for _, row in df.iterrows()
    ]
    GenericEvent.objects.bulk_create(events, batch_size=10_000, ignore_conflicts=True)


def _needs_retrain(mdl_path: Path) -> bool:
    sentinel = mdl_path.parent / ".force_retrain"
    if not mdl_path.exists():
        return True
    if sentinel.exists():
        sentinel.unlink(missing_ok=True)
        return True
    mtime = datetime.fromtimestamp(mdl_path.stat().st_mtime)
    return datetime.utcnow() - mtime > _RETTRAIN_AFTER


def _drift_detect(old_scores: np.ndarray, new_scores: np.ndarray) -> bool:
    if len(old_scores) < 500:
        return False
    _stat, p = ks_2samp(old_scores, new_scores)
    return p < _DRIFT_PVAL


def _add_temporal(df: pd.DataFrame) -> pd.DataFrame:
    if "timestamp" in df.columns and "hour" not in df.columns:
        ts = pd.to_datetime(df["timestamp"], errors="coerce")
        df["hour"] = ts.dt.hour.astype("Int8")
        df["dow"] = ts.dt.dayofweek.astype("Int8")
    return df


def _score_pending(ds: DataSource, cfg: DetectorConfig) -> None:
    pending_qs = GenericEvent.objects.filter(
        datasource_alias=ds.alias, scoredevent__isnull=True
    ).order_by("timestamp")[: cfg.batch_size]
    if not pending_qs:
        return

    df_raw = pd.DataFrame(pending_qs.values())
    features = _add_temporal(df_raw["payload"].apply(pd.Series))

    vec_path, mdl_path = paths(ds.alias)
    vec = load(vec_path)
    mdl = load(mdl_path)

    retrain = vec is None or mdl is None or _needs_retrain(mdl_path)

    if retrain:
        vec = build_vectorizer(features)
        X = vec.fit_transform(features)

        mdl = IsolationForest(
            n_estimators=200,
            max_samples=max(int(len(features) ** 0.5), 256),
            contamination=cfg.sensitivity or 0.02,
            max_features=1.0,
            random_state=42,
            warm_start=True,
        ).fit(X)

        save(vec, vec_path)
        save(mdl, mdl_path)
    else:
        X = vec.transform(features)

        if mdl.n_estimators < _MAX_TREES:
            mdl.set_params(
                n_estimators=min(mdl.n_estimators + _NEW_TREES_EACH_RUN, _MAX_TREES),
                warm_start=True,
            )
            mdl.fit(X)
            save(mdl, mdl_path)

    scores = mdl.decision_function(X)
    q = max(min(cfg.sensitivity, 0.5), 1e-4)
    cutoff = float(np.quantile(scores, q)) + cfg.threshold
    flags = scores < cutoff

    ScoredEvent.objects.bulk_create(
        [
            ScoredEvent(
                raw_id=row["id"],
                score=float(s),
                is_anom=bool(f),
                algo_ver="iforest_2.0",
            )
            for row, s, f in zip(df_raw.to_dict("records"), scores, flags)
        ],
        batch_size=10_000,
    )

    hist_scores = (
        ScoredEvent.objects.filter(raw__datasource_alias=ds.alias)
        .order_by("-scored_at")
        .values_list("score", flat=True)[:5000]
    )
    if _drift_detect(np.array(hist_scores, dtype=float), scores):
        (mdl_path.parent / ".force_retrain").touch()


@shared_task
def score_new_data() -> None:
    cfg = DetectorConfig.objects.first()
    if not cfg or not cfg.enabled:
        return

    for ds in DataSource.objects.filter(is_active=True):
        cfg = ds.config
        if not cfg.enabled:
            continue
        ensure_django_alias(ds)

        df = _fetch_new_rows(ds)
        if not df.empty:
            _bulk_ingest(ds, df)

        _score_pending(ds, cfg)


def _clean(v):
    if isinstance(v, (pd.Timestamp, datetime)):
        return v.isoformat()
    if isinstance(v, (np.generic,)):
        return v.item()
    if pd.isna(v):
        return None
    return v
