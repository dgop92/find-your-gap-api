from .base import *

DEBUG = True

SECRET_KEY = "_"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "github_actions",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

SCHEDULE_DATA_FUNCTION = "base.core.register_user.get_schedule_data_for_development"
