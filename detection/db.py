from django.db import connections, DEFAULT_DB_ALIAS
from django.conf import settings
import sqlalchemy as sa

def get_sqla_engine(ds):
    url = sa.engine.URL.create(
        drivername=f"{ds.engine}+pymysql",
        username  =ds.user or settings.DATABASES[DEFAULT_DB_ALIAS]["USER"],
        password  =ds.password or settings.DATABASES[DEFAULT_DB_ALIAS]["PASSWORD"],
        host      =ds.host,
        port      =ds.port,
        database  =ds.name,
    )
    return sa.create_engine(url, pool_pre_ping=True)

def ensure_django_alias(ds):
    if ds.alias in settings.DATABASES:
        return
    settings.DATABASES[ds.alias] = {
        "ENGINE"  : f"django.db.backends.{ds.engine}",
        "NAME"    : ds.name,
        "USER"    : ds.user,
        "PASSWORD": ds.password,
        "HOST"    : ds.host,
        "PORT"    : str(ds.port),
        "OPTIONS" : {"init_command": "SET sql_mode='STRICT_ALL_TABLES'"},
    }
    connections.ensure_defaults(ds.alias)
    connections.prepare_test_settings(ds.alias)
