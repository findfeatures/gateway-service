from gateway.exceptions.base import remote_error


@remote_error("accounts.exceptions.stripe.UnableToCreateCheckoutSession")
class UnableToCreateCheckoutSession(Exception):
    pass
