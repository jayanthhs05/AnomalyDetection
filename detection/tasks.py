from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import pandas as pd
from celery import shared_task
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Max
from sqlalchemy import text
from sklearn.ensemble import IsolationForest

from .db_utils import ensure_django_alias, get_sqla_engine
from .models import DataSource, DetectorConfig, GenericEvent, ScoredEvent
from .vectorize import build_vectorizer
from .utils_model import load, save, paths


_RETTRAIN_AFTER = timedelta(days=7)
_MAX_SAMPLES = 20_000


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

    events: List[GenericEvent] = [
        GenericEvent(
            datasource_alias=ds.alias,
            timestamp=row[ds.ts_column],
            series_key=_series_key(row, ds.series_cols),
            payload=row.to_dict(),
        )
        for _, row in df.iterrows()
    ]

    try:
        GenericEvent.objects.bulk_create(
            events, batch_size=10_000, ignore_conflicts=True
        )
    except IntegrityError:

        pass


def _needs_retrain(mdl_path: Path) -> bool:

    if not mdl_path.exists():
        return True
    mtime = datetime.fromtimestamp(mdl_path.stat().st_mtime)
    return datetime.utcnow() - mtime > _RETTRAIN_AFTER


def _score_pending(ds: DataSource, cfg: DetectorConfig) -> None:

    pending_qs = GenericEvent.objects.filter(
        datasource_alias=ds.alias, scoredevent__isnull=True
    ).order_by("timestamp")[: cfg.batch_size]
    if not pending_qs:
        return

    df_raw = pd.DataFrame(pending_qs.values())
    features = df_raw["payload"].apply(pd.Series)

    vec_path, mdl_path = paths(ds.alias)
    vec = load(vec_path)
    mdl = load(mdl_path)

    if vec is None or mdl is None or _needs_retrain(mdl_path):
        vec = build_vectorizer(features)
        X = vec.fit_transform(features)

        mdl = IsolationForest(
            n_estimators=400,
            max_samples=min(_MAX_SAMPLES, len(features)),
            contamination="auto",
            max_features=1.0,
            random_state=42,
        ).fit(X)

        save(vec, vec_path)
        save(mdl, mdl_path)
    else:
        X = vec.transform(features)

    scores = mdl.decision_function(X)
    cutoff = mdl.offset_ + cfg.threshold
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


@shared_task
def score_new_data() -> None:
    cfg = DetectorConfig.objects.first()
    if not cfg or not cfg.enabled:
        return

    for ds in DataSource.objects.filter(is_active=True):
        ensure_django_alias(ds)
