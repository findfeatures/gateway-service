import logging
from functools import wraps

import jwt
from gateway.exceptions.users_exceptions import UserNotAuthorised
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from nameko import config


logger = logging.getLogger(__name__)


def jwt_required():
    """
        Entrypoint decorator that requires a valid jwt in the Authorization header.
        Returns UserNotAuthorised() exception if jwt is not valid
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            request = args[1]

            # https://security.stackexchange.com/a/205701
            jwt_header = request.headers.get("Authorization")

            if not jwt_header:
                raise UserNotAuthorised()
            try:
                jwt.decode(jwt_header, config.get("JWT_SECRET"), algorithms=["HS256"])
            except ExpiredSignatureError:
                # todo: mainly here incase in the future we want to handle this
                # better for the flow for a user
                raise UserNotAuthorised()
            except InvalidTokenError:
                raise UserNotAuthorised()

            return fn(*args, **kwargs)

        return decorator

    return wrapper
