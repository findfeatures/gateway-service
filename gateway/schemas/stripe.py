from marshmallow import Schema, fields


class CreateStripeCheckoutSessionRequest(Schema):
    plan = fields.String(required=True)
    success_url = fields.String(required=True)
    cancel_url = fields.String(required=True)
    project_id = fields.Integer(required=True)


class CreateStripeCheckoutSessionResponse(Schema):
    session_id = fields.String(required=True)
