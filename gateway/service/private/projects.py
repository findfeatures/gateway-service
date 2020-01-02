from gateway.entrypoints import http
from gateway.service.base import ServiceMixin
from gateway.utils.jwt_utils import jwt_required
from werkzeug import Response


class ProjectsServiceMixin(ServiceMixin):
    @jwt_required()
    @http("POST", "/v1/projects", expected_exceptions=(None,))
    def create_project(self, request):

        return Response(mimetype="application/json")
