import json

import pytest
import httpx
from jsonschema import validate

from clients.http_users_client import HttpUsersClient
from config import API_BASE_URL, ADMIN_API_TOKEN, API_TOKEN, USER_API_TOKEN
from tests.http_test_support import (
    ERROR_SCHEMA,
    USERS_LIST_SCHEMA,
    USER_SCHEMA,
    assert_error_body_contract,
    assert_user_contract,
    make_http_users_client,
)


pytestmark = pytest.mark.api


def test_http_get_existing_user_returns_200(http_users_client):
    response = http_users_client.get_user(1)

    assert response.status_code == 200
    assert response.json()["email"] == "egor@example.com"


def test_http_get_missing_user_returns_404(http_users_client):
    response = http_users_client.get_user(999)

    assert response.status_code == 404
    assert "message" in response.json()


def test_http_create_valid_user_returns_201(http_users_client):
    response = http_users_client.create_user({
        "name": "Anna",
        "email": "anna@example.com",
    })

    assert response.status_code == 201
    assert response.json()["name"] == "Anna"
    assert response.json()["email"] == "anna@example.com"


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Anna"},
        {"email": "anna@example.com"},
        {},
    ],
)
def test_http_create_invalid_payloads_return_400(http_users_client, payload):
    response = http_users_client.create_user(payload)

    assert response.status_code == 400
    assert "message" in response.json()


def test_http_delete_existing_user_returns_204(http_users_client):
    response = http_users_client.delete_user(1)

    assert response.status_code == 204


def test_http_search_users_by_email_returns_200(http_users_client):
    response = http_users_client.search_users(email="anna@example.com")

    assert response.status_code == 200
    assert response.json()[0]["email"] == "anna@example.com"


def test_http_search_users_unknown_email_returns_empty_list(http_users_client):
    response = http_users_client.search_users(email="unknown@example.com")

    assert response.status_code == 200
    assert response.json() == []


def test_http_search_users_response_has_request_id_header(http_users_client):
    response = http_users_client.search_users(email="anna@example.com")

    assert response.headers["X-Request-Id"] == "test-request-123"


@pytest.mark.auth
def test_get_current_user_without_token_returns_401(http_users_client):
    response = http_users_client.get_current_user()

    assert response.status_code == 401
    assert_error_body_contract(response.json())


@pytest.mark.auth
def test_get_current_user_with_wrong_token_returns_403():
    client = make_http_users_client(
        headers={"Authorization": "Bearer wrong-token"},
    )

    try:
        response = client.get_current_user()
    finally:
        client.http_client.close()

    assert response.status_code == 403
    assert_error_body_contract(response.json())


@pytest.mark.auth
def test_get_current_user_with_token_returns_200(authenticated_http_users_client):
    response = authenticated_http_users_client.get_current_user()

    assert response.status_code == 200
    assert response.json()["email"] == "egor@example.com"


@pytest.mark.auth
@pytest.mark.contract
def test_get_current_user_with_token_matches_user_contract(
    authenticated_http_users_client,
):
    response = authenticated_http_users_client.get_current_user()

    assert response.status_code == 200
    assert_user_contract(response.json())


@pytest.mark.auth
def test_get_admin_users_without_token_returns_401(http_users_client):
    response = http_users_client.get_admin_users()

    assert response.status_code == 401
    assert_error_body_contract(response.json())


@pytest.mark.auth
def test_get_admin_users_with_wrong_token_returns_401():
    client = make_http_users_client(
        headers={"Authorization": "Bearer wrong-token"},
    )

    try:
        response = client.get_admin_users()
    finally:
        client.http_client.close()

    assert response.status_code == 401
    assert_error_body_contract(response.json())


@pytest.mark.auth
def test_get_admin_users_with_user_token_returns_403(user_http_users_client):
    response = user_http_users_client.get_admin_users()

    assert response.status_code == 403
    assert_error_body_contract(response.json())


@pytest.mark.auth
def test_get_admin_users_with_admin_token_returns_200(admin_http_users_client):
    response = admin_http_users_client.get_admin_users()

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.auth
@pytest.mark.contract
def test_get_admin_users_with_admin_token_matches_users_list_schema(
    admin_http_users_client,
):
    response = admin_http_users_client.get_admin_users()

    assert response.status_code == 200
    validate(instance=response.json(), schema=USERS_LIST_SCHEMA)


@pytest.mark.auth
@pytest.mark.parametrize(
    "authorization_header, expected_status_code, expected_message",
    [
        (None, 401, "Authentication required"),
        ("Bearer wrong-token", 401, "Invalid token"),
        (f"Bearer {USER_API_TOKEN}", 403, "Admin permission required"),
        (f"Bearer {ADMIN_API_TOKEN}", 200, None),
    ],
    ids=["no-token", "wrong-token", "user-token", "admin-token"],
)
def test_get_admin_users_access_control_matrix(
    authorization_header,
    expected_status_code,
    expected_message,
):
    headers = {}

    if authorization_header is not None:
        headers = {"Authorization": authorization_header}

    client = make_http_users_client(headers=headers)

    try:
        response = client.get_admin_users()
    finally:
        client.http_client.close()

    assert response.status_code == expected_status_code

    if expected_message is not None:
        assert response.json()["message"] == expected_message

    if expected_status_code == 200:
        assert isinstance(response.json(), list)
        assert len(response.json()) == 2


@pytest.mark.contract
def test_http_get_existing_user_matches_user_contract(http_users_client):
    response = http_users_client.get_user(1)

    assert response.status_code == 200
    assert_user_contract(response.json())


@pytest.mark.contract
def test_http_search_users_returns_list_of_user_contracts(http_users_client):
    response = http_users_client.search_users(email="anna@example.com")
    users = response.json()

    assert response.status_code == 200
    assert isinstance(users, list)

    for user in users:
        assert_user_contract(user)


@pytest.mark.contract
def test_http_get_missing_user_matches_error_contract(http_users_client):
    response = http_users_client.get_user(999)
    error_body = response.json()

    assert response.status_code == 404
    assert_error_body_contract(error_body)
    assert error_body["error"] == "Not Found"


@pytest.mark.contract
def test_http_create_valid_user_matches_user_contract(http_users_client):
    response = http_users_client.create_user({
        "name": "Anna",
        "email": "anna@example.com",
    })

    assert response.status_code == 201
    assert_user_contract(response.json())


@pytest.mark.contract
def test_http_create_invalid_payload_matches_error_contract(http_users_client):
    response = http_users_client.create_user({
        "name": "Anna",
    })
    error_body = response.json()

    assert response.status_code == 400
    assert_error_body_contract(error_body)
    assert error_body["error"] == "Bad Request"


@pytest.mark.contract
def test_http_get_existing_user_matches_json_schema(http_users_client):
    response = http_users_client.get_user(1)

    assert response.status_code == 200
    validate(instance=response.json(), schema=USER_SCHEMA)


@pytest.mark.contract
def test_http_search_users_matches_json_schema(http_users_client):
    response = http_users_client.search_users(email="anna@example.com")

    assert response.status_code == 200
    validate(instance=response.json(), schema=USERS_LIST_SCHEMA)


@pytest.mark.contract
def test_http_get_missing_user_matches_error_json_schema(http_users_client):
    response = http_users_client.get_user(999)

    assert response.status_code == 404
    validate(instance=response.json(), schema=ERROR_SCHEMA)


@pytest.mark.contract
def test_http_create_valid_user_matches_json_schema(http_users_client):
    response = http_users_client.create_user({
        "name": "Anna",
        "email": "anna@example.com",
    })

    assert response.status_code == 201
    validate(instance=response.json(), schema=USER_SCHEMA)


@pytest.mark.contract
def test_http_create_invalid_payload_matches_error_json_schema(http_users_client):
    response = http_users_client.create_user({
        "name": "Anna",
    })

    assert response.status_code == 400
    validate(instance=response.json(), schema=ERROR_SCHEMA)


def test_get_user_sends_get_to_expected_path(captured_http_users_client):
    client, captured_requests = captured_http_users_client

    client.get_user(1)
    request = captured_requests[0]

    assert request.method == "GET"
    assert request.url.path == "/users/1"


def test_create_user_sends_post_to_users_path(captured_http_users_client):
    client, captured_requests = captured_http_users_client

    client.create_user({
        "name": "Anna",
        "email": "anna@example.com",
    })
    request = captured_requests[0]

    assert request.method == "POST"
    assert request.url.path == "/users"


def test_create_user_sends_json_body(captured_http_users_client):
    client, captured_requests = captured_http_users_client
    user_data = {
        "name": "Anna",
        "email": "anna@example.com",
    }

    client.create_user(user_data)
    request = captured_requests[0]
    request_body = json.loads(request.content.decode("utf-8"))

    assert request_body["name"] == user_data["name"]
    assert request_body["email"] == user_data["email"]


def test_delete_user_sends_delete_to_expected_path(captured_http_users_client):
    client, captured_requests = captured_http_users_client

    client.delete_user(1)
    request = captured_requests[0]

    assert request.method == "DELETE"
    assert request.url.path == "/users/1"


def test_search_users_sends_get_to_users_path(captured_http_users_client):
    client, captured_requests = captured_http_users_client

    client.search_users(email="anna@example.com")
    request = captured_requests[0]

    assert request.method == "GET"
    assert request.url.path == "/users"


def test_search_users_sends_query_params(captured_http_users_client):
    client, captured_requests = captured_http_users_client

    client.search_users(email="anna@example.com", limit=10)
    request = captured_requests[0]

    assert request.url.path == "/users"
    assert request.url.params.get("email") == "anna@example.com"
    assert request.url.params.get("limit") == "10"


def test_create_user_sends_json_content_type_header(captured_http_users_client):
    client, captured_requests = captured_http_users_client

    client.create_user({
        "name": "Anna",
        "email": "anna@example.com",
    })
    request = captured_requests[0]

    assert request.headers["content-type"].startswith("application/json")


@pytest.mark.auth
def test_get_current_user_sends_authorization_header():
    captured_requests = []

    def handler(request):
        captured_requests.append(request)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    with httpx.Client(
        base_url=API_BASE_URL,
        transport=transport,
        headers=headers,
    ) as http_client:
        client = HttpUsersClient(http_client)
        client.get_current_user()

    request = captured_requests[0]

    assert request.headers["Authorization"] == f"Bearer {API_TOKEN}"


@pytest.mark.auth
def test_get_admin_users_sends_authorization_header():
    captured_requests = []

    def handler(request):
        captured_requests.append(request)
        return httpx.Response(200, json=[])

    transport = httpx.MockTransport(handler)
    headers = {"Authorization": f"Bearer {ADMIN_API_TOKEN}"}

    with httpx.Client(
        base_url=API_BASE_URL,
        transport=transport,
        headers=headers,
    ) as http_client:
        client = HttpUsersClient(http_client)
        client.get_admin_users()

    request = captured_requests[0]

    assert request.headers["Authorization"] == f"Bearer {ADMIN_API_TOKEN}"
