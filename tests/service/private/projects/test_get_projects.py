import json

from gateway.exceptions.users import UserNotAuthorised
from gateway.service import GatewayService
from mock import ANY, call
from nameko.containers import ServiceContainer
from nameko.testing.services import replace_dependencies


"""

class GetProjectResponse(Schema):
    id = fields.String(required=True)
    name = fields.String(required=True)
    created_datetime_utc = fields.String(required=True)


class GetProjectsResponse(Schema):
    projects = fields.Nested(GetProjectResponse, many=True, required=True)

"""


def test_get_projects(config, web_session, mock_jwt_token):
    container = ServiceContainer(GatewayService)
    accounts = replace_dependencies(container, "accounts_rpc")
    container.start()

    user_id = 1

    mock_jwt_token.return_value = {"user_id": user_id}

    accounts.get_verified_projects.return_value = [
        {
            "id": 1,
            "name": "test_project",
            "created_datetime_utc": "2019-01-01T00:00:00Z",
        },
        {
            "id": 2,
            "name": "test_project_2",
            "created_datetime_utc": "2019-01-02T00:00:00Z",
        },
    ]

    response = web_session.get("/v1/projects")

    assert accounts.get_verified_projects.call_args == call(user_id)

    assert response.status_code == 200
    assert response.json() == {
        "projects": [
            {
                "id": 1,
                "name": "test_project",
                "created_datetime_utc": "2019-01-01T00:00:00Z",
            },
            {
                "id": 2,
                "name": "test_project_2",
                "created_datetime_utc": "2019-01-02T00:00:00Z",
            },
        ]
    }
