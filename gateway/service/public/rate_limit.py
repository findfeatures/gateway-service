import datetime
import json

from gateway.entrypoints import http
from gateway.lua_scripts import RATE_LIMIT_QUERY
from gateway.service.base import ServiceMixin
from werkzeug import Response
from gateway.utils.redis_utils import hash_auth_token


class RateLimitServiceMixin(ServiceMixin):
    @http("GET", "/v1/rate-limit", rate_limit=5000, auth_required=True)
    def rate_limit(self, request):
        end_timestamp = int(datetime.datetime.utcnow().timestamp() * 1000)

        auth_token = request.auth_token

        result = {}

        endpoints = ["/v1/rate-limit"]

        for endpoint in endpoints:
            script = self.redis.register_script(RATE_LIMIT_QUERY)

            num_of_existing_scores = script(
                keys=[f"{hash_auth_token(auth_token)}:{endpoint}"], args=[end_timestamp]
            )

            rate_limit = int(self.redis.get(f"rate-limit:{endpoint}"))

            result[endpoint] = {
                "limit": rate_limit,
                "remaining": rate_limit - num_of_existing_scores,
            }

        return Response(json.dumps(result), mimetype="application/json")
