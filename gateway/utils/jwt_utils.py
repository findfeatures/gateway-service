import logging
from functools import wraps

import jwt
from gateway.exceptions.users import UserNotAuthorised
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from nameko import config


logger = logging.getLogger(__name__)


def jwt_required():
    """
        Entrypoint decorator that requires a valid jwt in the Authorization header.
        Returns UserNotAuthorised() exception if jwt is not valid.

        Injects 'jwt_data' into the request

        Example:
            inside entrypoint handler:
                request.jwt_data == YOUR JWT DATA
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            request = args[1]

            # https://security.stackexchange.com/a/205701
            jwt_header = get_jwt_header(request)

            if not jwt_header:
                raise UserNotAuthorised()
            try:
                jwt_data = jwt.decode(
                    jwt_header, config.get("JWT_SECRET"), algorithms=["HS256"]
                )
                request.jwt_data = jwt_data
                args = list(args)
                args[1] = request
                # todo: inject into request here!
            except ExpiredSignatureError:
                # todo: mainly here incase in the future we want to handle this
                # better for the flow for a user
                raise UserNotAuthorised()
            except InvalidTokenError:
                raise UserNotAuthorised()

            return fn(*args, **kwargs)

        return decorator

    return wrapper


def get_jwt_header(request):
    # so we can mock this easier
    return request.headers.get("Authorization")
