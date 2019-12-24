import json

from gateway.exceptions.users_exceptions import UserAlreadyExists
from gateway.service import GatewayService
from mock import ANY, call
from nameko.containers import ServiceContainer
from nameko.testing.services import replace_dependencies


def tests_users_create(config, web_session):
    container = ServiceContainer(GatewayService)
    users = replace_dependencies(container, "users_rpc")
    container.start()

    users.create_user.return_value = {"user_id": 1}

    email = "test@google.com"
    password = "password"
    display_name = "test"

    request = {"email": email, "password": password, "display_name": display_name}

    response = web_session.post("/user", data=json.dumps(request))

    assert users.create_user.call_args == call(request)

    assert response.status_code == 200

    assert response.text == ""


def tests_users_create_already_exists(config, web_session):
    container = ServiceContainer(GatewayService)
    users = replace_dependencies(container, "users_rpc")
    container.start()

    users.create_user.side_effect = UserAlreadyExists()

    email = "test@google.com"
    password = "password"
    display_name = "test"

    request = {"email": email, "password": password, "display_name": display_name}

    response = web_session.post("/user", data=json.dumps(request))

    assert response.status_code == 409
    assert response.json() == {"error": "USER_ALREADY_EXISTS", "message": ""}
