from gateway.dependencies.redis.provider import Redis
from nameko.rpc import RpcProxy


class ServiceMixin:
    name = "gateway"

    users_rpc = RpcProxy("users")
    redis = Redis()
