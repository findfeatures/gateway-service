import datetime
import logging

import redis
from gateway.exceptions.base import RateLimitExceeded
from gateway.lua_scripts import RATE_LIMIT
from nameko import config


logger = logging.getLogger(__name__)


def get_redis_connection():
    redis_url = config.get("REDIS_URL")

    if not redis_url:
        raise ValueError("REDIS_URL must be defined")

    return redis.from_url(redis_url)


def check_rate_limit(auth_token, url, rate_limit_per_minute):
    r = get_redis_connection()

    # sorted sets in redis FTW!
    # Using Lua makes sure that no other redis client can execute the script parallelly.
    milliseconds_since_epoch = int(datetime.datetime.utcnow().timestamp() * 1000)

    script = r.register_script(RATE_LIMIT)
    result = script(
        keys=[f"{auth_token}:{url}"],
        args=[milliseconds_since_epoch, rate_limit_per_minute],
    )

    num_of_existing_scores, result = result.decode("utf-8").split(":")
    num_of_existing_scores = int(num_of_existing_scores)

    if num_of_existing_scores == 0 and result == "limit-exceeded":
        raise RateLimitExceeded()

    return rate_limit_per_minute - num_of_existing_scores


def store_redis_rate_limit_for_url(url, rate_limit):
    r = get_redis_connection()

    r.set(f"rate-limit:{url}", rate_limit)
