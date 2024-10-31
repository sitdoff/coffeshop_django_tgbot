from .base import *

SECRET_KEY = "VERY STRONG SECRET_KEY"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "testing_db.sqlite3",
    }
}
