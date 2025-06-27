import joblib, os, tempfile
from pathlib import Path
from django.conf import settings
from django.utils.text import slugify
import pickle

STORE = Path(settings.BASE_DIR, "model_store")
STORE.mkdir(exist_ok=True)

def _atomic_dump(obj, path: Path):
    tmp_fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    os.close(tmp_fd)
    try:
        joblib.dump(obj, tmp_name)
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)

def save(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_dump(obj, path)

def load(path: Path):
    if not path.exists():
        return None
    try:
        return joblib.load(path)
    except (EOFError, pickle.UnpicklingError, ValueError):
        path.unlink(missing_ok=True)
        return None

def paths(alias):
    safe = slugify(alias, allow_unicode=False)
    root = Path(settings.BASE_DIR, "model_store", safe).resolve()
    (root).mkdir(parents=True, exist_ok=True)

    store_root = (Path(settings.BASE_DIR) / "model_store").resolve()
    if store_root not in root.parents:
        raise ValueError("Invalid alias – would escape model_store")

    return root / "vectorizer.joblib", root / "iforest.joblib"