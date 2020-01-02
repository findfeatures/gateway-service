from gateway.service.private.projects import ProjectsServiceMixin
from gateway.service.private.users import UsersServiceMixin
from gateway.service.public.health_check import HealthCheckServiceMixin
from gateway.service.public.rate_limit import RateLimitServiceMixin


class GatewayService(
    HealthCheckServiceMixin,
    UsersServiceMixin,
    ProjectsServiceMixin,
    RateLimitServiceMixin,
):
    pass
