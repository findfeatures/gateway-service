import datetime
import logging

from gateway.dependencies.redis.lua_scripts import RATE_LIMIT
from gateway.dependencies.redis.utils import get_redis_connection, hash_identifier
from gateway.exceptions.base import RateLimitExceeded
from nameko import config
from nameko.extensions import DependencyProvider


logger = logging.getLogger(__name__)

MONITORING_STREAM_NAME = "MONITORING_STREAM"


def store_redis_rate_limit_for_url(url, rate_limit):
    r = get_redis_connection()

    r.set(f"rate-limit:{url}", rate_limit)


def redis_send_monitor(monitor_name, data=None):
    if data is None:
        data = {}

    # add __MONITOR_NAME to data dict
    if "__MONITOR_NAME" in data:
        raise ValueError("__MONITOR_NAME can only be defined once.")

    data["__MONITOR_NAME"] = monitor_name

    r = get_redis_connection()

    r.xadd(MONITORING_STREAM_NAME, data)


def check_rate_limit(identifier, url, rate_limit, sensitive=True):
    if sensitive:
        identifier = hash_identifier(identifier)

    r = get_redis_connection()

    # Using Lua makes sure that no other redis
    # client can execute the script parallelly.
    milliseconds_since_epoch = int(datetime.datetime.utcnow().timestamp() * 1000)

    script = r.register_script(RATE_LIMIT)
    result = script(
        keys=[f"{identifier}:{url}"], args=[milliseconds_since_epoch, rate_limit]
    )

    existing_scores, result = result.decode("utf-8").split(":")
    existing_scores = int(existing_scores)

    if existing_scores == rate_limit and result == "limit-exceeded":
        raise RateLimitExceeded()

    # -1 because num_of_existing_scores is before we insert another 1
    return rate_limit - existing_scores - 1


class Redis(DependencyProvider):
    def __init__(self, **options):
        self.client = None
        self.options = {"decode_responses": True}
        self.options.update(options)

    def setup(self):
        self.redis_uri = config.get("REDIS_URL")

    def start(self):
        self.client = get_redis_connection(self.redis_uri, **self.options)

    def stop(self):
        self.client = None

    def kill(self):
        self.client = None

    def get_dependency(self, worker_ctx):
        return self.client
