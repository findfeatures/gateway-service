from marshmallow import Schema, fields


class AuthUserRequest(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)


class UserCheckRequest(Schema):
    email = fields.String(required=True)


class UserAuthResponse(Schema):
    JWT = fields.String(required=True)


class CreateUserRequest(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)
    display_name = fields.String(required=True)


class VerifyUserTokenRequest(Schema):
    email = fields.String(required=True)
    token = fields.String(required=True)


class ResendUserTokenEmailRequest(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)
