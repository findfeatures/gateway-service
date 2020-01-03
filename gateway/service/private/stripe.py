import json

from gateway.entrypoints import http
from gateway.exceptions.stripe import UnableToCreateCheckoutSession
from gateway.schemas import stripe as stripe_schemas
from gateway.service.base import ServiceMixin
from gateway.utils.jwt_utils import jwt_required
from werkzeug import Response


class StripeServiceMixin(ServiceMixin):
    @jwt_required()
    @http(
        "POST",
        "/v1/stripe/checkout-session",
        expected_exceptions=(UnableToCreateCheckoutSession,),
    )
    def create_stripe_checkout_session(self, request):

        checkout_session_details = stripe_schemas.CreateStripeCheckoutSessionRequest().load(
            json.loads(request.data)
        )

        jwt_data = request.jwt_data

        session_id = self.accounts_rpc.create_stripe_checkout_session(
            {
                "user_id": jwt_data["user_id"],
                "email": jwt_data["email"],
                "plan": checkout_session_details["plan"],
                "success_url": checkout_session_details["success_url"],
                "cancel_url": checkout_session_details["cancel_url"],
            }
        )

        return Response(
            stripe_schemas.CreateStripeCheckoutSessionResponse().dumps(
                {"session_id": session_id}
            ),
            mimetype="application/json",
        )
