from marshmallow import Schema, fields


class GetProjectResponse(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    created_datetime_utc = fields.String(required=True)


class GetProjectsResponse(Schema):
    projects = fields.Nested(GetProjectResponse, many=True, required=True)
