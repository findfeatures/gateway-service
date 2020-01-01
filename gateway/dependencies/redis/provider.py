from nameko import config
from nameko.extensions import DependencyProvider
from redis import StrictRedis as _StrictRedis


class Redis(DependencyProvider):
    def __init__(self, **options):
        self.client = None
        self.options = {"decode_responses": True}
        self.options.update(options)

    def setup(self):
        self.redis_uri = config.get("REDIS_URL")

    def start(self):
        self.client = _StrictRedis.from_url(self.redis_uri, **self.options)

    def stop(self):
        self.client = None

    def kill(self):
        self.client = None

    def get_dependency(self, worker_ctx):
        return self.client
