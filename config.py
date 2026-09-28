import os


DEFAULT_USER = {
    "id": 1,
    "name": "Egor",
    "email": "egor@example.com",
}

CREATED_USER_NAME = "Nina"
CREATED_USER_EMAIL = "nina@example.com"

API_TIMEOUT_SECONDS = 30
ENVIRONMENT = "local"
API_BASE_URL = "https://api.example.test"
API_TOKEN = os.getenv("API_TOKEN", "test-token")
USER_API_TOKEN = os.getenv("USER_API_TOKEN", "user-token")
ADMIN_API_TOKEN = os.getenv("ADMIN_API_TOKEN", "admin-token")
