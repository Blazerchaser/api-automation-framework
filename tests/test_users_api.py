from copy import deepcopy

import pytest


def test_get_existing_user_returns_200(users_client):
    response = users_client.get_user(1)

    assert response["status_code"] == 200


def test_get_existing_user_has_required_fields(users_client):
    response = users_client.get_user(1)
    required_fields = ["id", "name", "email"]

    for field in required_fields:
        assert field in response["json"]


def test_get_missing_user_returns_404(users_client):
    response = users_client.get_user(999)

    assert response["status_code"] == 404
    assert "message" in response["json"]


def test_create_valid_user_returns_201(users_client):
    user_data = {
        "name": "Anna",
        "email": "anna@example.com",
    }

    response = users_client.create_user(user_data)

    assert response["status_code"] == 201
    assert response["json"]["name"] == "Anna"
    assert response["json"]["email"] == "anna@example.com"


def test_create_user_without_email_returns_400(users_client):
    user_data = {
        "name": "Anna",
    }

    response = users_client.create_user(user_data)

    assert response["status_code"] == 400
    assert "message" in response["json"]


@pytest.mark.parametrize(
    "payload, expected_status_code",
    [
        ({"name": "Anna"}, 400),
        ({"email": "anna@example.com"}, 400),
        ({}, 400),
        (None, 400),
    ],
)
def test_create_user_with_invalid_payloads_returns_400(
    users_client,
    payload,
    expected_status_code,
):
    users_before = deepcopy(users_client.users)
    response = users_client.create_user(payload)
    error_body = response["json"]

    assert response["status_code"] == expected_status_code
    assert isinstance(error_body, dict)
    assert "error" in error_body
    assert "message" in error_body
    assert isinstance(error_body["error"], str)
    assert isinstance(error_body["message"], str)
    assert error_body["error"] == "Bad Request"
    assert users_client.users == users_before


def test_create_user_can_be_fetched_by_id(users_client, user_data_factory):
    user_data = user_data_factory()

    create_response = users_client.create_user(user_data)
    created_id = create_response["json"]["id"]
    get_response = users_client.get_user(created_id)

    assert create_response["status_code"] == 201
    assert get_response["status_code"] == 200
    assert get_response["json"]["name"] == user_data["name"]
    assert get_response["json"]["email"] == user_data["email"]


def test_created_users_get_unique_ids(users_client, user_data_factory):
    first_response = users_client.create_user(user_data_factory())
    second_response = users_client.create_user(user_data_factory())

    assert first_response["status_code"] == 201
    assert second_response["status_code"] == 201
    assert first_response["json"]["id"] != second_response["json"]["id"]


def test_delete_existing_user_returns_204(users_client):
    create_response = users_client.create_user({
        "name": "Olga",
        "email": "olga@example.com",
    })
    created_id = create_response["json"]["id"]

    delete_response = users_client.delete_user(created_id)

    assert delete_response["status_code"] == 204
    assert delete_response["json"] is None


def test_deleted_user_cannot_be_fetched(users_client):
    create_response = users_client.create_user({
        "name": "Olga",
        "email": "olga@example.com",
    })
    created_id = create_response["json"]["id"]

    users_client.delete_user(created_id)
    get_response = users_client.get_user(created_id)

    assert get_response["status_code"] == 404


def test_delete_missing_user_returns_404(users_client):
    response = users_client.delete_user(999)

    assert response["status_code"] == 404
    assert "message" in response["json"]


def test_delete_already_deleted_user_returns_404(users_client):
    create_response = users_client.create_user({
        "name": "Olga",
        "email": "olga@example.com",
    })
    created_id = create_response["json"]["id"]

    users_client.delete_user(created_id)
    second_delete_response = users_client.delete_user(created_id)

    assert second_delete_response["status_code"] == 404
    assert "message" in second_delete_response["json"]


def test_created_user_fixture_can_be_fetched(users_client, created_user):
    response = users_client.get_user(created_user["id"])

    assert response["status_code"] == 200
    assert response["json"]["email"] == created_user["email"]


def test_created_user_fixture_has_required_fields(created_user):
    required_fields = ["id", "name", "email"]

    for field in required_fields:
        assert field in created_user
