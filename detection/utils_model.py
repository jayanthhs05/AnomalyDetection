import joblib, os
from pathlib import Path
from django.conf import settings

STORE = Path(settings.BASE_DIR, "model_store")
STORE.mkdir(exist_ok=True)

VEC_FILE  = STORE / "vectorizer.joblib"
MOD_FILE  = STORE / "iforest.joblib"

def save(obj, path): joblib.dump(obj, path)
def load(path):      return joblib.load(path) if path.exists() else None

def paths(alias):
    STORE = Path(settings.BASE_DIR, "model_store", alias)
    STORE.mkdir(parents=True, exist_ok=True)
    return STORE / "vectorizer.joblib", STORE / "iforest.joblib"