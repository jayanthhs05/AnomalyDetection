import sqlalchemy as sa
from django.core.exceptions import ValidationError
from .db_utils import get_sqla_engine


def validate_source(ds):
    eng = get_sqla_engine(ds)

    with eng.connect() as cn:
        preview = (
            cn.execute(sa.text(f"SELECT * FROM ({ds.sql}) AS t LIMIT 1"))
            .mappings()
            .first()
        )

    if ds.ts_column not in preview:
        raise ValidationError(f"'{ds.ts_column}' column is missing in result-set")

    if ds.series_cols:
        missing = [c for c in ds.series_cols.split(",") if c.strip() not in preview]
        if missing:
            raise ValidationError(f"Series column(s) {missing} not present")

    if not preview:
        raise ValidationError("Query returned no rows — unable to infer schema")
