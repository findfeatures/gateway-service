from gateway.exceptions.base import remote_error


@remote_error("accounts.exceptions.users.UserNotAuthorised")
class UserNotAuthorised(Exception):
    pass


@remote_error("accounts.exceptions.users.UserAlreadyExists")
class UserAlreadyExists(Exception):
    pass


@remote_error("accounts.exceptions.users.UserNotVerified")
class UserNotVerified(Exception):
    pass
