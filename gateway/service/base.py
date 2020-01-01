from gateway.dependencies.redis.provider import Redis
from nameko.rpc import RpcProxy


class ServiceMixin:
    name = "gateway"

    accounts_rpc = RpcProxy("accounts")
    redis = Redis()
