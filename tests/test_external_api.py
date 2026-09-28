import os

import pytest
import httpx


EXTERNAL_USER_URL = "https://jsonplaceholder.typicode.com/users/1"


@pytest.fixture
def external_api_enabled():
    if os.getenv("RUN_EXTERNAL_API_TESTS") != "1":
        pytest.skip("Set RUN_EXTERNAL_API_TESTS=1 to run external API tests")


@pytest.mark.external
def test_external_get_user_returns_200(external_api_enabled):
    response = httpx.get(EXTERNAL_USER_URL, timeout=5.0)

    assert response.status_code == 200


@pytest.mark.external
def test_external_get_user_has_basic_contract(external_api_enabled):
    response = httpx.get(EXTERNAL_USER_URL, timeout=5.0)
    body = response.json()

    assert isinstance(body, dict)
    assert "id" in body
    assert "name" in body
    assert "email" in body
    assert isinstance(body["id"], int)
    assert isinstance(body["name"], str)
    assert isinstance(body["email"], str)
