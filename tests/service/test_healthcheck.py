from gateway.service import GatewayService
from nameko.containers import ServiceContainer


def test_health_check(config, web_session):
    container = ServiceContainer(GatewayService)
    container.start()

    response = web_session.get("/health-check")
    assert response.status_code == 200
