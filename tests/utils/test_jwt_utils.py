import jwt
import pytest
from gateway.exceptions.users_exceptions import UserNotAuthorised
from gateway.utils.jwt_utils import jwt_required
from mock import Mock
from nameko import config as nameko_config


class FakeService:
    @jwt_required()
    def fake_function(self, request):
        return "I worked"


def test_jwt_required_works_correctly_on_class(config):

    valid_token = jwt.encode(
        {"test": "123"}, nameko_config.get("JWT_SECRET"), algorithm="HS256"
    )

    mock_request = Mock()

    mock_request.headers = {"Authorization": valid_token.decode("utf-8")}

    service = FakeService()

    result = service.fake_function(mock_request)

    assert result == "I worked"


def test_jwt_required_raises_error_if_missing_header():
    mock_request = Mock()

    mock_request.headers = {}

    service = FakeService()

    with pytest.raises(UserNotAuthorised):
        service.fake_function(mock_request)


def test_jwt_required_raises_error_if_jwt_invalid(config):
    mock_request = Mock()

    mock_request.headers = {"Authorization": "random token!"}

    service = FakeService()

    with pytest.raises(UserNotAuthorised):
        service.fake_function(mock_request)


def test_jwt_required_raises_error_if_jwt_expired(config):
    mock_request = Mock()

    # exp is the expiry time epoch.
    # (1577208307 ~ 2019 - 12 - 24 @ 5:30pm UTC Christmas Eve)
    jwt.encode(
        {"test": "123", "exp": 1577208307}, nameko_config.get("JWT_SECRET"), algorithm="HS256"
    )

    mock_request.headers = {"Authorization": "random token!"}

    service = FakeService()

    with pytest.raises(UserNotAuthorised):
        service.fake_function(mock_request)
