from gateway.entrypoints import http
from gateway.schemas import projects as projects_schemas
from gateway.service.base import ServiceMixin
from gateway.utils.jwt_utils import jwt_required
from werkzeug import Response


class ProjectsServiceMixin(ServiceMixin):
    @jwt_required()
    @http("GET", "/v1/projects")
    def get_projects(self, request):
        import time
        time.sleep(2)
        jwt_data = request.jwt_data

        projects = self.accounts_rpc.get_verified_projects(jwt_data["user_id"])

        return Response(
            projects_schemas.GetProjectsResponse().dumps({"projects": projects}),
            mimetype="application/json",
        )
