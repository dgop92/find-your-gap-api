from decouple import config

from .base import *

DEBUG = True

SECRET_KEY = config("SECRET_KEY")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

API_REGISTER_DATA_FUNC = "base.tests.register_utils.get_api_register_data"
UNINORTE_SCHEDULE_API = "https://mihorario.herokuapp.com/api/v1/authentications"
