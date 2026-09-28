from config import API_TIMEOUT_SECONDS, ENVIRONMENT


def test_environment_is_local():
    assert ENVIRONMENT == "local"


def test_api_timeout_is_positive():
    assert API_TIMEOUT_SECONDS > 0
