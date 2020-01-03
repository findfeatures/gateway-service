from gateway.service import GatewayService
from mock import call
from nameko.containers import ServiceContainer
from nameko.testing.services import replace_dependencies


def test_check_user_exists_false(config, web_session):
    container = ServiceContainer(GatewayService)
    accounts = replace_dependencies(container, "accounts_rpc")
    container.start()

    accounts.user_already_exists.return_value = False

    email = "test@google.com"

    response = web_session.head(f"/v1/user/{email}")

    assert accounts.user_already_exists.call_args == call(email)

    assert response.status_code == 200


def test_check_user_exists_true(config, web_session):
    container = ServiceContainer(GatewayService)
    accounts = replace_dependencies(container, "accounts_rpc")
    container.start()

    accounts.user_already_exists.return_value = True

    email = "test@google.com"

    response = web_session.head(f"/v1/user/{email}")

    assert accounts.user_already_exists.call_args == call(email)

    assert response.status_code == 409
    # heads dont return any thing
    assert response.text == ""
