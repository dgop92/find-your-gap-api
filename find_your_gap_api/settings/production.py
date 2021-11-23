import dj_database_url
from decouple import Csv, config

from .base import *

SECRET_KEY = config("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default=[])
CORS_ORIGIN_WHITELIST = config("CORS_ORIGIN_WHITELIST", cast=Csv(), default=[])

MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")
MIDDLEWARE.insert(2, "whitenoise.middleware.WhiteNoiseMiddleware")

db_from_env = dj_database_url.config(conn_max_age=600)

DATABASES = {"default": db_from_env}

API_REGISTER_DATA_FUNC = "base.core.register_user.get_api_register_data"
