import logging
import os
from os import environ, path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

def secret_key(secret_file: str) -> str | None:
    if secret_file and os.path.isfile(secret_file):
        with open(secret_file, "r") as file:
            return file.read().rstrip()
    return None

SECRET_KEY = secret_key(environ.get("SECRET_KEY_FILE")) or environ.get("SECRET_KEY")

SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(environ.get("DATABASE_PATH") or "sand-track.sqlite")

logger.info(f"Using DB {SQLALCHEMY_DATABASE_URI}")
UPLOAD_FOLDER = "/tmp"