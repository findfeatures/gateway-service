import datetime

from gateway.entrypoints import http
from gateway.service.base import ServiceMixin


class HealthCheckServiceMixin(ServiceMixin):
    @http("GET", "/v1/health-check", rate_limit=150, auth_required=True)
    def health_check(self, request):

        self.redis.set("health-check", datetime.datetime.utcnow().isoformat())
        return 200, "OK"
