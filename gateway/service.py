import json
import time

from gateway import schemas
from gateway.entrypoints import http
from gateway.exceptions.users_exceptions import UserAlreadyExists, UserNotAuthorised
from nameko.rpc import RpcProxy
from werkzeug import Response


class GatewayService:
    """
        Service acts as a gateway to other services over http.
    """

    name = "gateway"

    users_rpc = RpcProxy("users")

    @http("GET", "/health-check")
    def health_check(self, request):
        return 200, "OK"

    @http("POST", "/user/auth", expected_exceptions=(UserNotAuthorised,))
    def users_auth(self, request):
        """
        Provides authentication for a user, will return
        a valid JWT if the user is successfully logged in.
        """
        user_auth_details = schemas.UserAuthRequest().load(json.loads(request.data))
        jwt_result = self.users_rpc.auth_user(
            user_auth_details["email"], user_auth_details["password"]
        )

        return Response(
            schemas.UserAuthResponse().dumps(jwt_result), mimetype="application/json"
        )

    @http("POST", "/user", expected_exceptions=(UserAlreadyExists,))
    def users_create(self, request):
        """
        Allows the creation of a new user.
        """
        create_user_details = schemas.CreateUserRequest().load(json.loads(request.data))

        user_id = self.users_rpc.create_user(create_user_details)

        return Response(mimetype="application/json")
