from gateway.exceptions.base import remote_error


@remote_error("users.exceptions.users.UserNotAuthorised")
class UserNotAuthorised(Exception):
    pass


@remote_error("users.exceptions.users.UserAlreadyExists")
class UserAlreadyExists(Exception):
    pass


@remote_error("users.exceptions.users.UserNotVerified")
class UserNotVerified(Exception):
    pass
