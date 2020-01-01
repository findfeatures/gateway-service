import datetime
import json

from gateway.entrypoints import http
from gateway.lua_scripts import RATE_LIMIT_QUERY
from gateway.service.base import ServiceMixin
from werkzeug import Response


class RateLimitServiceMixin(ServiceMixin):
    @http("GET", "/v1/rate-limit", auth_required=True)
    def rate_limit(self, request):
        auth_token = request.auth_token

        cursor, keys = self.redis.scan(match=f"{auth_token}:*")

        result = {}

        end_timestamp = int(datetime.datetime.utcnow().timestamp() * 1000)
        for key in keys:
            token, endpoint = key.split(":")

            script = self.redis.register_script(RATE_LIMIT_QUERY)

            num_of_existing_scores = script(keys=[f"{key}"], args=[end_timestamp])

            rate_limit = int(self.redis.get(f"rate-limit:{endpoint}"))

            result[endpoint] = {
                "limit": rate_limit,
                "remaining": rate_limit - num_of_existing_scores,
            }

        return Response(json.dumps(result), mimetype="application/json")
