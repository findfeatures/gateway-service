import datetime
import logging

import redis
from gateway.exceptions.base import RateLimitExceeded
from nameko import config


logger = logging.getLogger(__name__)


def check_rate_limit(token, unique_identifier, rate_limit_per_minute):
    redis_url = config.get("REDIS_URL")

    if not redis_url:
        raise ValueError("REDIS_URL must be defined")

    r = redis.from_url(redis_url)

    # sorted sets in redis FTW!
    # Using Lua makes sure that no other redis client can execute the script parallelly.
    # modified from here:
    # https://medium.com/@sahiljadon/rate-limiting-using-redis-lists-and-sorted-sets-9b42bc192222
    lua = """
    --[[
        remove any scores for the at key between 0 and 1 minute before the 
        current request time
    ]]--
    redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, ARGV[1] - 60 * 1000 )
    
    --[[
        check if number of scores in the key are < requests allowed and if so
        add the score to the sorted set
    ]]--
    local num_of_existing_scores = tonumber(redis.call('ZCARD', KEYS[1]))
    
    if num_of_existing_scores < tonumber(ARGV[2])
    then
        redis.call('ZADD', KEYS[1], ARGV[1], ARGV[1])
        return num_of_existing_scores
    else
        return num_of_existing_scores
    end
    """

    milliseconds_since_epoch = int(datetime.datetime.utcnow().timestamp() * 1000)
    script = r.register_script(lua)

    num_of_existing_scores = script(
        keys=[f"{token}:{unique_identifier}"],
        args=[milliseconds_since_epoch, rate_limit_per_minute],
    )

    if num_of_existing_scores == 0:
        raise RateLimitExceeded()

    return rate_limit_per_minute - num_of_existing_scores
