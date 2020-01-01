from gateway.service import GatewayService
from nameko.containers import ServiceContainer
from nameko.testing.services import replace_dependencies


def test_health_check(config, web_session):
    container = ServiceContainer(GatewayService)
    redis = replace_dependencies(container, "redis")
    container.start()

    redis.set.return_value = "1"

    response = web_session.get("/health-check")
    assert response.status_code == 200
