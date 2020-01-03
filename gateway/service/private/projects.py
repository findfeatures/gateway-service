from gateway.entrypoints import http
from gateway.service.base import ServiceMixin
from gateway.utils.jwt_utils import jwt_required
from werkzeug import Response


class ProjectsServiceMixin(ServiceMixin):
    @jwt_required()
    @http("GET", "/v1/projects")
    def get_projects(self, request):

        jwt_data = request.jwt_data

        projects = self.accounts_rpc.get_verified_projects(jwt_data["user_id"])

        return Response(mimetype="application/json")

    @jwt_required()
    @http("POST", "/v1/projects", expected_exceptions=(None,))
    def create_project(self, request):

        return Response(mimetype="application/json")
