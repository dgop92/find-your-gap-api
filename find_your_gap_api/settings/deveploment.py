import dj_database_url
from decouple import config

from .base import *

DEBUG = True

SECRET_KEY = config("SECRET_KEY")

db_from_env = dj_database_url.config(conn_max_age=600)

if db_from_env:
    DATABASES = {"default": db_from_env}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }


SCHEDULE_DATA_FUNCTION = "base.core.register_user.get_schedule_data_for_development"
DEL_UNVERIFIED_SECRET_CODE = "DEV-CODE"
