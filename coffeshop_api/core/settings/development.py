import os

from core.settings.base import *

from .base import *

# load_dotenv()

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ALLOWED_HOSTS = ["web", "localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
