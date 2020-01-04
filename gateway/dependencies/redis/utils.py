import walrus
from nameko import config
from passlib.hash import pbkdf2_sha256


def hash_identifier(identifier):
    return pbkdf2_sha256.hash(identifier)


def get_redis_connection():
    redis_url = config.get("REDIS_URL", "redis://127.0.0.1:6379/0")

    return walrus.Database().from_url(redis_url)
