import datetime
import json
from functools import partial
from types import FunctionType

from gateway.dependencies.redis.provider import (
    check_rate_limit,
    redis_send_monitor,
    store_redis_rate_limit_for_url,
)
from gateway.exceptions.base import (
    AuthorizationHeaderMissing,
    RateLimitExceeded,
    UnauthorizedRequest,
)
from gateway.exceptions.users_exceptions import (
    UserAlreadyExists,
    UserNotAuthorised,
    UserNotVerified,
)
from marshmallow import ValidationError
from nameko import config
from nameko.exceptions import BadRequest, safe_for_serialization
from nameko.extensions import register_entrypoint
from nameko.web.handlers import HttpRequestHandler
from werkzeug import Response


class HttpEntrypoint(HttpRequestHandler):
    """
    Custom HTTPEntrypoint that:
        - Adds CORS support by default to requests
        - Add rate_limit and private_rate_limit option
            (rate_limit is per minute on a rolling window)
        - Add rate_limit headers to requests that are rate limited
        - Add authorization option (requires Authorization header with valid api token)
        - Better exception handling to catch errors we care about and
            return sensible messages.
    """

    # standard mapped errors which are always caught
    standard_mapped_errors = {
        ValidationError: (400, "VALIDATION_ERROR"),
        UserNotAuthorised: (401, "USER_NOT_AUTHORISED"),
        BadRequest: (400, "BAD_REQUEST"),
        AuthorizationHeaderMissing: (400, "AUTHORIZATION_HEADER_MISSING"),
        UnauthorizedRequest: (401, "UNAUTHORISED_REQUEST"),
        RateLimitExceeded: (429, "RATE_LIMIT_EXCEEDED"),
    }

    mapped_errors = {
        UserAlreadyExists: (409, "USER_ALREADY_EXISTS"),
        UserNotVerified: (418, "USER_NOT_VERIFIED"),
    }

    def __init__(self, method, url, expected_exceptions=(), **kwargs):
        super().__init__(method, url, expected_exceptions=expected_exceptions)

        cors = config.get("DEFAULT_CORS", "*").split(",")

        self.allowed_origin = kwargs.get("origin", cors)
        self.allowed_methods = kwargs.get("methods", ["*"])
        self.allow_credentials = kwargs.get("credentials", True)

        self.standard_mapped_errors_tuple = tuple(self.standard_mapped_errors.keys())

        self.rate_limit = kwargs.get("rate_limit")
        self.private_rate_limit = kwargs.get("private_rate_limit")
        self.auth_required = kwargs.get("auth_required", False)

        if self.rate_limit is not None and not self.auth_required:
            raise ValueError(
                "if public rate limit is defined then auth_required must be true"
            )

        if self.rate_limit and self.private_rate_limit:
            raise ValueError(
                "cant define an entrypoint with a public and private rate limit"
            )

        if self.rate_limit or self.private_rate_limit:
            store_redis_rate_limit_for_url(
                self.url, self.rate_limit or self.private_rate_limit
            )

    def handle_request(self, request):
        start = datetime.datetime.utcnow()

        response = self._handle_request(request)

        duration = datetime.datetime.utcnow() - start

        redis_send_monitor(
            "API_REQUEST",
            {
                "method": request.method,
                "url": self.url,
                "duration": duration.total_seconds(),
                "status": response.status,
                "status_code": response.status_code,
                "remote_addr": request.remote_addr,
            },
        )

        return response

    def _handle_request(self, request):
        rate_limit_left = 0
        self.request = request

        if request.method == "OPTIONS":
            return self.response_from_result(result="")

        if self.auth_required:
            try:
                auth_token = self._get_auth_token_from_header(request)
                request.auth_token = auth_token
                if self.rate_limit:
                    rate_limit_left = self._check_rate_limit(identifier=auth_token)
            except (
                UnauthorizedRequest,
                AuthorizationHeaderMissing,
                RateLimitExceeded,
            ) as exc:
                response = self.response_from_exception(exc)
                response = self._add_rate_limit(response, rate_limit_left)
                return response

        if self.private_rate_limit:
            try:
                rate_limit_left = self._check_rate_limit(
                    identifier=request.remote_addr, sensitive=False
                )
            except (RateLimitExceeded,) as exc:
                response = self.response_from_exception(exc)

                response = self._add_rate_limit(response, rate_limit_left)
                return response
        response = super().handle_request(request)
        response = self._add_rate_limit(response, rate_limit_left)
        return response

    def response_from_result(self, *args, **kwargs):
        response = super(HttpEntrypoint, self).response_from_result(*args, **kwargs)
        response = self._add_cors(response)
        return response

    def response_from_exception(self, exc):
        status_code, error_code = 500, "UNEXPECTED_ERROR"

        if isinstance(exc, self.expected_exceptions) or isinstance(
            exc, self.standard_mapped_errors_tuple
        ):
            if type(exc) in self.standard_mapped_errors:
                status_code, error_code = self.standard_mapped_errors[type(exc)]
            elif type(exc) in self.mapped_errors:
                status_code, error_code = self.mapped_errors[type(exc)]
            else:
                status_code = 400
                error_code = "BAD_REQUEST"

        response = Response(
            json.dumps({"error": error_code, "message": safe_for_serialization(exc)}),
            status=status_code,
            mimetype="application/json",
        )
        response = self._add_cors(response)

        return response

    def _add_cors(self, response):
        response.headers.add(
            "Access-Control-Allow-Headers",
            self.request.headers.get("Access-Control-Request-Headers"),
        )
        response.headers.add(
            "Access-Control-Allow-Credentials", str(self.allow_credentials).lower()
        )
        response.headers.add(
            "Access-Control-Allow-Methods", ",".join(self.allowed_methods)
        )
        response.headers.add(
            "Access-Control-Allow-Origin", ",".join(self.allowed_origin)
        )
        return response

    def _add_rate_limit(self, response, rate_limit_left):

        if self.rate_limit or self.private_rate_limit:
            response.headers.add(
                "X-Rate-Limit", self.rate_limit or self.private_rate_limit
            )
            response.headers.add("X-Rate-Limit-Left", rate_limit_left)

        return response

    def _check_rate_limit(self, identifier="", sensitive=True):
        rate_limit_left = check_rate_limit(
            identifier,
            self.url,
            self.rate_limit or self.private_rate_limit,
            sensitive=sensitive,
        )
        return rate_limit_left

    @staticmethod
    def _get_auth_token_from_header(request):
        token = request.headers.get("Authorization")

        if not token:
            raise AuthorizationHeaderMissing("Authorization header is required.")

        # if token == "web-app" then this request is from the web-app
        # when we change and add actual tokens this would be authenticated here
        if token != "web-app":
            raise UnauthorizedRequest("Request is unauthorized.")

        return token

    @classmethod
    def decorator(cls, *args, **kwargs):
        """
        We're overriding the decorator classmethod to allow it to register an options
        route for each standard REST call. This saves us from manually defining OPTIONS
        routes for each CORs enabled endpoint
        """

        def registering_decorator(fn, args, kwargs):
            instance = cls(*args, **kwargs)
            register_entrypoint(fn, instance)
            if instance.method in ("GET", "POST", "DELETE", "PUT", "HEAD") and (
                "*" in instance.allowed_methods
                or instance.method in instance.allowed_methods
            ):
                options_args = ["OPTIONS"] + list(args[1:])
                options_instance = cls(*options_args, **kwargs)
                register_entrypoint(fn, options_instance)
            return fn

        if len(args) == 1 and isinstance(args[0], FunctionType):
            # usage without arguments to the decorator:
            # @foobar
            # def spam():
            #     pass
            return registering_decorator(args[0], args=(), kwargs={})
        else:
            # usage with arguments to the decorator:
            # @foobar('shrub', ...)
            # def spam():
            #     pass
            return partial(registering_decorator, args=args, kwargs=kwargs)


http = HttpEntrypoint.decorator
