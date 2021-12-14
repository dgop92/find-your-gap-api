import dj_database_url
from decouple import Csv, config

from .base import *

SECRET_KEY = config("SECRET_KEY")

DEBUG = False

MIDDLEWARE.insert(2, "whitenoise.middleware.WhiteNoiseMiddleware")

db_from_env = dj_database_url.config(conn_max_age=600)

DATABASES = {"default": db_from_env}

SCHEDULE_DATA_FUNCTION = "base.core.register_user.get_schedule_data_from_uni_api"
