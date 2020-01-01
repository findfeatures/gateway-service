import datetime

from gateway.entrypoints import http
from gateway.service.base import ServiceMixin


class HealthCheckServiceMixin(ServiceMixin):
    @http("GET", "/health-check")
    def health_check(self, request):

        self.redis.set("health-check", datetime.datetime.utcnow().isoformat())

        return 200, "OK"
