import json

import httpx

from clients.http_users_client import HttpUsersClient
from config import API_BASE_URL, ADMIN_API_TOKEN, API_TOKEN, USER_API_TOKEN


def mock_users_handler(request):
    if request.method == "GET" and request.url.path == "/admin/users":
        authorization = request.headers.get("Authorization")

        if authorization is None:
            return httpx.Response(
                401,
                json={
                    "error": "Unauthorized",
                    "message": "Authentication required",
                },
            )

        if authorization == f"Bearer {USER_API_TOKEN}":
            return httpx.Response(
                403,
                json={
                    "error": "Forbidden",
                    "message": "Admin permission required",
                },
            )

        if authorization == f"Bearer {ADMIN_API_TOKEN}":
            return httpx.Response(
                200,
                json=[
                    {
                        "id": 1,
                        "name": "Egor",
                        "email": "egor@example.com",
                    },
                    {
                        "id": 2,
                        "name": "Anna",
                        "email": "anna@example.com",
                    },
                ],
            )

        return httpx.Response(
            401,
            json={
                "error": "Unauthorized",
                "message": "Invalid token",
            },
        )

    if request.method == "GET" and request.url.path == "/me":
        authorization = request.headers.get("Authorization")

        if authorization is None:
            return httpx.Response(
                401,
                json={
                    "error": "Unauthorized",
                    "message": "Authentication required",
                },
            )

        if authorization != f"Bearer {API_TOKEN}":
            return httpx.Response(
                403,
                json={
                    "error": "Forbidden",
                    "message": "Forbidden",
                },
            )

        return httpx.Response(
            200,
            json={
                "id": 1,
                "name": "Egor",
                "email": "egor@example.com",
            },
        )

    if request.method == "GET" and request.url.path == "/users":
        headers = {"X-Request-Id": "test-request-123"}

        if request.url.params.get("email") == "anna@example.com":
            return httpx.Response(
                200,
                headers=headers,
                json=[
                    {
                        "id": 2,
                        "name": "Anna",
                        "email": "anna@example.com",
                    }
                ],
            )

        return httpx.Response(200, headers=headers, json=[])

    if request.method == "GET" and request.url.path == "/users/1":
        return httpx.Response(
            200,
            json={
                "id": 1,
                "name": "Egor",
                "email": "egor@example.com",
            },
        )

    if request.method == "GET" and request.url.path == "/users/999":
        return httpx.Response(
            404,
            json={
                "error": "Not Found",
                "message": "User not found",
            },
        )

    if request.method == "POST" and request.url.path == "/users":
        user_data = json.loads(request.content.decode("utf-8"))

        if not user_data or "name" not in user_data or "email" not in user_data:
            return httpx.Response(
                400,
                json={
                    "error": "Bad Request",
                    "message": "Name and email are required",
                },
            )

        return httpx.Response(
            201,
            json={
                "id": 2,
                "name": user_data["name"],
                "email": user_data["email"],
            },
        )

    if request.method == "DELETE" and request.url.path == "/users/1":
        return httpx.Response(204)

    return httpx.Response(
        404,
        json={
            "error": "Not Found",
            "message": "Route not found",
        },
    )


def make_http_users_client(headers=None):
    transport = httpx.MockTransport(mock_users_handler)
    http_client = httpx.Client(
        base_url=API_BASE_URL,
        transport=transport,
        headers=headers,
    )

    return HttpUsersClient(http_client)


def assert_user_contract(user):
    assert isinstance(user, dict)
    assert "id" in user
    assert "name" in user
    assert "email" in user
    assert isinstance(user["id"], int)
    assert isinstance(user["name"], str)
    assert isinstance(user["email"], str)
    assert "@" in user["email"]


def assert_error_body_contract(error_body):
    assert isinstance(error_body, dict)
    assert "error" in error_body
    assert "message" in error_body
    assert isinstance(error_body["error"], str)
    assert isinstance(error_body["message"], str)


USER_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "email"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string"},
    },
}


ERROR_SCHEMA = {
    "type": "object",
    "required": ["error", "message"],
    "properties": {
        "error": {"type": "string"},
        "message": {"type": "string"},
    },
}


USERS_LIST_SCHEMA = {
    "type": "array",
    "items": USER_SCHEMA,
}
