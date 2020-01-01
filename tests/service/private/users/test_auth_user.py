import json

from gateway.exceptions.users_exceptions import UserNotAuthorised
from gateway.service import GatewayService
from mock import ANY, call
from nameko.containers import ServiceContainer
from nameko.testing.services import replace_dependencies


def test_auth_user(config, web_session):
    container = ServiceContainer(GatewayService)
    users = replace_dependencies(container, "accounts_rpc")
    container.start()

    users.auth_user.return_value = {"JWT": "test"}

    email = "test@google.com"
    password = "password"

    response = web_session.post(
        "/v1/user/auth", data=json.dumps({"email": email, "password": password})
    )

    assert users.auth_user.call_args == call(email, password)

    assert response.status_code == 200
    assert response.json() == {"JWT": "test"}


def test_auth_user_not_authorised(config, web_session):
    container = ServiceContainer(GatewayService)
    users = replace_dependencies(container, "accounts_rpc")
    container.start()

    users.auth_user.side_effect = UserNotAuthorised()

    response = web_session.post(
        "/v1/user/auth", data=json.dumps({"email": "email", "password": "password"})
    )

    assert response.status_code == 401
    assert response.json() == {"error": "USER_NOT_AUTHORISED", "message": ""}


def test_auth_user_incorrect_schema(config, web_session):
    container = ServiceContainer(GatewayService)
    users = replace_dependencies(container, "accounts_rpc")
    container.start()

    users.auth_user.side_effect = UserNotAuthorised()

    response = web_session.post("/v1/user/auth", data=json.dumps({}))

    assert response.status_code == 400
    assert response.json() == {"error": "VALIDATION_ERROR", "message": ANY}
