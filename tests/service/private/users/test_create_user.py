import json

from gateway.exceptions.users_exceptions import UserAlreadyExists
from gateway.service import GatewayService
from mock import call
from nameko.containers import ServiceContainer
from nameko.testing.services import replace_dependencies


def test_create_user(config, web_session):
    container = ServiceContainer(GatewayService)
    users = replace_dependencies(container, "accounts_rpc")
    container.start()

    users.create_user.return_value = {"user_id": 1}

    email = "test@google.com"
    password = "password"
    display_name = "test"

    request = {"email": email, "password": password, "display_name": display_name}

    response = web_session.post("/v1/user", data=json.dumps(request))

    assert users.create_user.call_args == call(request)

    assert response.status_code == 200

    assert response.text == ""


def test_create_user_already_exists(config, web_session):
    container = ServiceContainer(GatewayService)
    users = replace_dependencies(container, "accounts_rpc")
    container.start()

    users.create_user.side_effect = UserAlreadyExists()

    email = "test@google.com"
    password = "password"
    display_name = "test"

    request = {"email": email, "password": password, "display_name": display_name}

    response = web_session.post("/v1/user", data=json.dumps(request))

    assert response.status_code == 409
    assert response.json() == {"error": "USER_ALREADY_EXISTS", "message": ""}
