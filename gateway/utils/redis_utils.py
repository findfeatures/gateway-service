import datetime
import logging
import os
import hashlib

import redis
from gateway.exceptions.base import RateLimitExceeded
from gateway.lua_scripts import RATE_LIMIT
from nameko import config


logger = logging.getLogger(__name__)


def get_redis_connection():
    # not ideal, but sometimes redis is needed before the tests are run
    # so we need to expose the REDIS_URL here too
    redis_url = config.get("REDIS_URL") or os.environ["REDIS_URL"]

    if redis_url is None:
        raise ValueError(
            "REDIS_URL must be either defined in the config or as an env variable (when running tests). Example: REDIS_URL=redis://127.0.0.1:6379/0"
        )

    return redis.from_url(redis_url)


def check_rate_limit(auth_token, url, rate_limit_per_hour):
    r = get_redis_connection()

    # sorted sets in redis FTW!
    # Using Lua makes sure that no other redis client can execute the script parallelly.
    milliseconds_since_epoch = int(datetime.datetime.utcnow().timestamp() * 1000)

    script = r.register_script(RATE_LIMIT)
    result = script(
        keys=[f"{hash_auth_token(auth_token)}:{url}"],
        args=[milliseconds_since_epoch, rate_limit_per_hour],
    )

    num_of_existing_scores, result = result.decode("utf-8").split(":")
    num_of_existing_scores = int(num_of_existing_scores)

    if num_of_existing_scores == rate_limit_per_hour and result == "limit-exceeded":
        raise RateLimitExceeded()

    # -1 because num_of_existing_scores is before we insert another 1
    return rate_limit_per_hour - num_of_existing_scores - 1


def store_redis_rate_limit_for_url(url, rate_limit):
    r = get_redis_connection()

    r.set(f"rate-limit:{url}", rate_limit)


def hash_auth_token(auth_token):
    return hashlib.sha224(auth_token.encode()).hexdigest()
