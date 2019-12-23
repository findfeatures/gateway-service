import json
from mock import ANY, call
from gateway.exceptions.users_exceptions import UserNotAuthorised
from gateway.service import GatewayService
from nameko.containers import ServiceContainer
from nameko.testing.services import replace_dependencies


def test_users_auth(config, web_session):
    container = ServiceContainer(GatewayService)
    users = replace_dependencies(container, "users_rpc")
    container.start()

    users.auth_user.return_value = {"JWT": "test"}

    email = "test@google.com"
    password = "password"

    response = web_session.post(
        "/user/auth", data=json.dumps({"email": email, "password": password})
    )

    assert users.auth_user.call_args == call(email, password)

    assert response.status_code == 200
    assert response.json() == {"JWT": "test"}


def test_users_auth_not_authorised(config, web_session):
    container = ServiceContainer(GatewayService)
    users = replace_dependencies(container, "users_rpc")
    container.start()

    users.auth_user.side_effect = UserNotAuthorised()

    response = web_session.post(
        "/user/auth", data=json.dumps({"email": "email", "password": "password"})
    )

    assert response.status_code == 401
    assert response.json() == {"error": "USER_NOT_AUTHORISED", "message": ""}


def test_users_auth_incorrect_schema(config, web_session):
    container = ServiceContainer(GatewayService)
    users = replace_dependencies(container, "users_rpc")
    container.start()

    users.auth_user.side_effect = UserNotAuthorised()

    response = web_session.post("/user/auth", data=json.dumps({}))

    assert response.status_code == 400
    assert response.json() == {
        "error": "VALIDATION_ERROR",
        "message": ANY,
    }
