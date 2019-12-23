from gateway.exceptions.base import remote_error


@remote_error("users.exceptions.UserNotAuthorised")
class UserNotAuthorised(Exception):
    pass


@remote_error("users.exceptions.UserAlreadyExists")
class UserAlreadyExists(Exception):
    pass
