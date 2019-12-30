import json

from gateway.exceptions.users_exceptions import UserNotAuthorised
from gateway.service import GatewayService
from mock import ANY, call
from nameko.containers import ServiceContainer
from nameko.testing.services import replace_dependencies


def test_users_token_valid(config, web_session):
    container = ServiceContainer(GatewayService)
    users = replace_dependencies(container, "users_rpc")
    container.start()

    users.verify_user.return_value = None

    email = "test@google.com"
    token = "token"

    response = web_session.post(
        "/user-token", data=json.dumps({"email": email, "token": token})
    )

    assert users.verify_user.call_args == call(email, token)

    assert response.status_code == 200


def test_users_token_invalid(config, web_session):
    container = ServiceContainer(GatewayService)
    users = replace_dependencies(container, "users_rpc")
    container.start()

    users.verify_user.side_effect = UserNotAuthorised()

    email = "test@google.com"
    token = "token"

    response = web_session.post(
        "/user-token", data=json.dumps({"email": email, "token": token})
    )

    assert users.verify_user.call_args == call(email, token)

    assert response.status_code == 401
    assert response.json() == {"error": "USER_NOT_AUTHORISED", "message": ""}


def test_users_token_incorrect_schema(config, web_session):
    container = ServiceContainer(GatewayService)
    users = replace_dependencies(container, "users_rpc")
    container.start()

    email = "test@google.com"

    response = web_session.post(
        "/user-token", data=json.dumps({"email": email})
    )

    assert response.status_code == 400
    assert response.json() == {"error": "VALIDATION_ERROR", "message": ANY}
