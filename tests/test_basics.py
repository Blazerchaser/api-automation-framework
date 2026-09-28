import pytest


def is_valid_email(email):
    if email.count("@") != 1:
        return False

    name, domain = email.split("@")

    return bool(name) and "." in domain


@pytest.fixture
def sample_user():
    return {
        "id": 1,
        "name": "Egor",
        "email": "egor@example.com",
        "is_active": True,
    }


def test_email_contains_at_symbol():
    email = "egor@example.com"

    assert "@" in email


def test_users_list_has_three_users():
    users = ["Egor", "Anna", "Ivan"]

    assert len(users) == 3


@pytest.mark.parametrize(
    "email, expected_result",
    [
        ("egor@example.com", True),
        ("invalid-email", False),
        ("user@domain.org", True),
        ("@example.com", False),
    ],
)
def test_email_validation_result(email, expected_result):
    assert is_valid_email(email) == expected_result


@pytest.mark.parametrize(
    "status_code, expected_success",
    [
        (200, True),
        (201, True),
        (404, False),
        (500, False),
    ],
)
def test_status_code_success_result(status_code, expected_success):
    is_success = status_code < 300

    assert is_success == expected_success


def test_sample_user_fixture_has_required_fields(sample_user):
    required_fields = ["id", "name", "email"]

    for field in required_fields:
        assert field in sample_user


@pytest.mark.smoke
def test_smoke_api_health_status_code():
    status_code = 200

    assert status_code == 200
