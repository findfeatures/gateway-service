import os

import walrus
from nameko import config
from passlib.hash import pbkdf2_sha256


def hash_identifier(identifier):
    return pbkdf2_sha256.hash(identifier)


def get_redis_connection(redis_url=None, **options):
    # not ideal, but sometimes redis is needed before the tests are run
    # so we need to expose the REDIS_URL here too
    redis_url = config.get("REDIS_URL") or os.environ["REDIS_URL"] or redis_url

    if redis_url is None:
        raise ValueError(
            "REDIS_URL must be either defined in the config or as an env "
            "variable (when running tests). Example: "
            "REDIS_URL=redis://127.0.0.1:6379/0"
        )

    return walrus.Database().from_url(redis_url, **options)
