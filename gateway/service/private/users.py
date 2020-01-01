import json
import time

from gateway import schemas
from gateway.entrypoints import http
from gateway.exceptions.users_exceptions import (
    UserAlreadyExists,
    UserNotAuthorised,
    UserNotVerified,
)
from gateway.service.base import ServiceMixin
from werkzeug import Response


class UsersServiceMixin(ServiceMixin):
    @http("POST", "/v1/user/auth", expected_exceptions=(UserNotVerified,))
    def auth_user(self, request):
        """
        Provides authentication for a user, will return
        a valid JWT if the user is successfully logged in.
        """
        user_auth_details = schemas.UserAuthRequest().load(json.loads(request.data))
        jwt_result = self.accounts_rpc.auth_user(
            user_auth_details["email"], user_auth_details["password"]
        )

        return Response(
            schemas.UserAuthResponse().dumps(jwt_result), mimetype="application/json"
        )

    @http("HEAD", "/v1/user/<email>", expected_exceptions=(UserAlreadyExists,))
    def check_user_exists(self, request, email):
        """
        Allows checking if a user already exists.
        """

        user_exists = self.accounts_rpc.user_already_exists(email)

        if user_exists:
            raise UserAlreadyExists()

        return Response(mimetype="application/json")

    @http("POST", "/v1/user", expected_exceptions=(UserAlreadyExists,))
    def create_user(self, request):
        """
        Allows the creation of a new user.
        """
        create_user_details = schemas.CreateUserRequest().load(json.loads(request.data))

        self.accounts_rpc.create_user(create_user_details)

        return Response(mimetype="application/json")

    @http("POST", "/v1/user-token", expected_exceptions=(UserNotAuthorised,))
    def verify_user_token(self, request):
        """
        Allows verifying a users token from signup.
        """

        user_token_details = schemas.UserTokenRequest().load(json.loads(request.data))

        self.accounts_rpc.verify_user(
            user_token_details["email"], user_token_details["token"]
        )

        return Response(mimetype="application/json")
