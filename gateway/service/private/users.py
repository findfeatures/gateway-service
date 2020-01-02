import json

from gateway.entrypoints import http
from gateway.exceptions.users_exceptions import (
    UserAlreadyExists,
    UserNotAuthorised,
    UserNotVerified,
)
from gateway.schemas import users as users_schemas
from gateway.service.base import ServiceMixin
from werkzeug import Response


class UsersServiceMixin(ServiceMixin):
    @http(
        "POST",
        "/v1/user/auth",
        expected_exceptions=(UserNotVerified,),
        private_rate_limit=60,
    )
    def auth_user(self, request):
        user_auth_details = users_schemas.AuthUserRequest().load(
            json.loads(request.data)
        )
        jwt_result = self.accounts_rpc.auth_user(
            user_auth_details["email"], user_auth_details["password"]
        )

        return Response(
            users_schemas.UserAuthResponse().dumps(jwt_result),
            mimetype="application/json",
        )

    @http(
        "HEAD",
        "/v1/user/<email>",
        expected_exceptions=(UserAlreadyExists,),
        private_rate_limit=60,
    )
    def check_user_exists(self, request, email):
        user_exists = self.accounts_rpc.user_already_exists(email)

        if user_exists:
            raise UserAlreadyExists()

        return Response(mimetype="application/json")

    @http(
        "POST",
        "/v1/user",
        expected_exceptions=(UserAlreadyExists,),
        private_rate_limit=60,
    )
    def create_user(self, request):
        create_user_details = users_schemas.CreateUserRequest().load(
            json.loads(request.data)
        )

        self.accounts_rpc.create_user(create_user_details)

        return Response(mimetype="application/json")

    @http(
        "POST",
        "/v1/user-token",
        expected_exceptions=(UserNotAuthorised,),
        private_rate_limit=60,
    )
    def verify_user_token(self, request):

        user_token_details = users_schemas.VerifyUserTokenRequest().load(
            json.loads(request.data)
        )

        self.accounts_rpc.verify_user(
            user_token_details["email"], user_token_details["token"]
        )

        return Response(mimetype="application/json")

    @http("POST", "/v1/resend-email", expected_exceptions=(), private_rate_limit=15)
    def resend_user_token_email(self, request):
        # todo: fill in expected_exceptions
        user_resend_details = users_schemas.ResendUserTokenEmailRequest().load(
            json.loads(request.data)
        )

        self.accounts_rpc.resend_user_token(
            user_resend_details["email"], user_resend_details["password"]
        )

        return Response(mimetype="application/json")
