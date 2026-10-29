from pathlib import Path


ROOT = Path(__file__).resolve().parent
INSTANCE = ROOT / "instance"
INSTANCE.mkdir(exist_ok=True)


class Config:
    SECRET_KEY = "parking-system-local"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{INSTANCE / 'parking.db'}"
    SQLALCHEMY_ENGINE_OPTIONS = {"use_insertmanyvalues": False}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_PATH = str(ROOT / "best.pt")
    SLIPS_DIR = str(ROOT / "static" / "slips")
