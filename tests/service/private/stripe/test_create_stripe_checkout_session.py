import json

from gateway.exceptions.stripe import UnableToCreateCheckoutSession
from gateway.service import GatewayService
from mock import call
from nameko.containers import ServiceContainer
from nameko.testing.services import replace_dependencies


def test_create_stripe_checkout_session_successful(config, web_session, mock_jwt_token):

    container = ServiceContainer(GatewayService)
    accounts = replace_dependencies(container, "accounts_rpc")
    container.start()

    accounts.create_stripe_checkout_session.return_value = "test"

    user_id = 1
    email = "test@google.com"
    plan = "plan_1"
    success_url = "http://success.com"
    cancel_url = "http://cancel.com"

    mock_jwt_token.return_value = {"user_id": user_id, "email": email}

    response = web_session.post(
        "/v1/stripe/checkout-session",
        data=json.dumps(
            {
                "plan": plan,
                "success_url": success_url,
                "cancel_url": cancel_url,
                "project_id": 1,
            }
        ),
    )

    assert accounts.create_stripe_checkout_session.call_args == call(
        {
            "user_id": user_id,
            "email": email,
            "plan": plan,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "project_id": 1,
        }
    )

    assert response.status_code == 200
    assert response.json() == {"session_id": "test"}


def test_create_stripe_checkout_session_unsuccessful(
    config, web_session, mock_jwt_token
):

    container = ServiceContainer(GatewayService)
    accounts = replace_dependencies(container, "accounts_rpc")
    container.start()

    accounts.create_stripe_checkout_session.side_effect = (
        UnableToCreateCheckoutSession()
    )
    user_id = 1
    email = "test@google.com"
    plan = "plan_1"
    success_url = "http://success.com"
    cancel_url = "http://cancel.com"

    mock_jwt_token.return_value = {"user_id": user_id, "email": email}

    response = web_session.post(
        "/v1/stripe/checkout-session",
        data=json.dumps(
            {
                "plan": plan,
                "success_url": success_url,
                "cancel_url": cancel_url,
                "project_id": 1,
            }
        ),
    )

    assert accounts.create_stripe_checkout_session.call_args == call(
        {
            "user_id": user_id,
            "email": email,
            "plan": plan,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "project_id": 1,
        }
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": "UNABLE_TO_CREATE_CHECKOUT_SESSION",
        "message": "",
    }
