from marshmallow import Schema, fields


class UserAuthRequest(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)


class UserAuthResponse(Schema):
    JWT = fields.String(required=True)


class CreateUserRequest(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)
    display_name = fields.String(required=True)
