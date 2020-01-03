import json

from gateway.exceptions.users import UserNotAuthorised
from gateway.service import GatewayService
from mock import call
from nameko.containers import ServiceContainer
from nameko.testing.services import replace_dependencies


def test_resend_user_token_email(config, web_session):
    container = ServiceContainer(GatewayService)
    accounts = replace_dependencies(container, "accounts_rpc")
    container.start()

    accounts.resend_user_token.return_value = None

    email = "test@google.com"
    password = "password"

    request = {"email": email, "password": password}

    response = web_session.post("/v1/user/resend-email", data=json.dumps(request))

    assert accounts.resend_user_token.call_args == call(email, password)

    assert response.status_code == 200

    assert response.text == ""


def test_resend_user_token_email_failure(config, web_session):
    container = ServiceContainer(GatewayService)
    accounts = replace_dependencies(container, "accounts_rpc")
    container.start()

    accounts.resend_user_token.side_effect = UserNotAuthorised()

    email = "test@google.com"
    password = "password"

    request = {"email": email, "password": password}

    response = web_session.post("/v1/user/resend-email", data=json.dumps(request))

    assert accounts.resend_user_token.call_args == call(email, password)

    assert response.status_code == 401

    assert response.json() == {"error": "USER_NOT_AUTHORISED", "message": ""}
