from uuid import uuid4

import httpx
import pytest

from clients.http_users_client import HttpUsersClient
from clients.users_client import UsersClient
from config import (
    API_BASE_URL,
    ADMIN_API_TOKEN,
    API_TOKEN,
    CREATED_USER_EMAIL,
    CREATED_USER_NAME,
    USER_API_TOKEN,
)
from tests.http_test_support import mock_users_handler


@pytest.fixture(scope="function")
def users_client():
    return UsersClient()


@pytest.fixture(scope="function")
def user_data_factory():
    def make_user_data():
        unique_value = uuid4().hex[:8]

        return {
            "name": f"Test User {unique_value}",
            "email": f"test.user.{unique_value}@example.com",
        }

    return make_user_data


@pytest.fixture
def created_user(users_client):
    create_response = users_client.create_user({
        "name": CREATED_USER_NAME,
        "email": CREATED_USER_EMAIL,
    })
    user = create_response["json"]

    yield user

    users_client.delete_user(user["id"])


@pytest.fixture
def http_users_client():
    transport = httpx.MockTransport(mock_users_handler)

    with httpx.Client(base_url=API_BASE_URL, transport=transport) as http_client:
        yield HttpUsersClient(http_client)


@pytest.fixture
def authenticated_http_users_client():
    transport = httpx.MockTransport(mock_users_handler)
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    with httpx.Client(
        base_url=API_BASE_URL,
        transport=transport,
        headers=headers,
    ) as http_client:
        yield HttpUsersClient(http_client)


@pytest.fixture
def user_http_users_client():
    transport = httpx.MockTransport(mock_users_handler)
    headers = {"Authorization": f"Bearer {USER_API_TOKEN}"}

    with httpx.Client(
        base_url=API_BASE_URL,
        transport=transport,
        headers=headers,
    ) as http_client:
        yield HttpUsersClient(http_client)


@pytest.fixture
def admin_http_users_client():
    transport = httpx.MockTransport(mock_users_handler)
    headers = {"Authorization": f"Bearer {ADMIN_API_TOKEN}"}

    with httpx.Client(
        base_url=API_BASE_URL,
        transport=transport,
        headers=headers,
    ) as http_client:
        yield HttpUsersClient(http_client)


@pytest.fixture
def captured_http_users_client():
    captured_requests = []

    def handler(request):
        captured_requests.append(request)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)

    with httpx.Client(base_url=API_BASE_URL, transport=transport) as http_client:
        yield HttpUsersClient(http_client), captured_requests
