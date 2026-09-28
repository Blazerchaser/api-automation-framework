# API Automation Framework

Minimal pytest project for learning QA Automation and simple API-like tests.

This project uses a learning mock/example instead of a real API server.

## Install dependencies

```bash
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run the full suite

```bash
.\.venv\Scripts\python.exe -m pytest -v
```

The external tests are skipped unless `RUN_EXTERNAL_API_TESTS=1` is set.

## Run the always-on suite (same selection as CI)

```powershell
.\.venv\Scripts\python.exe -m pytest -m "not external" -q
```

`.github/workflows/api.yml` runs this selection on `push` and `pull_request`
with Python 3.12. Green CI confirms the mock and local `127.0.0.1` tests;
it does not confirm that the external demo API is available. The workflow
still needs a GitHub-hosted run for validation.

## Run smoke tests

```bash
.\.venv\Scripts\python.exe -m pytest -m smoke -v
```

## Run marker groups

```bash
.\.venv\Scripts\python.exe -m pytest -m api -q
.\.venv\Scripts\python.exe -m pytest -m auth -q
.\.venv\Scripts\python.exe -m pytest -m contract -q
.\.venv\Scripts\python.exe -m pytest -m "api and not auth" -q
```

## Run external API tests

These tests call `https://jsonplaceholder.typicode.com`, an external demo API.
It can be unavailable or change outside this project.

```powershell
$env:RUN_EXTERNAL_API_TESTS="1"; .\.venv\Scripts\python.exe -m pytest -m external -v
Remove-Item Env:RUN_EXTERNAL_API_TESTS
```

## What this project demonstrates

- `fixture`: prepares reusable test data before a test runs.
- `parametrize`: takes test input from a parameter table instead of hardcoding it inside the test body.
- `marker`: marks tests as `smoke` or `external` so they can be run separately.
- `clients/users_client.py`: contains a small fake API client with `get_user` and `create_user`.
- `tests/test_users_api.py`: checks API-like responses with `status_code` and `json`.
- Stateful API flow: a created user is saved in the client state.
- After `create_user`, the same user can be fetched by the new `id`.
- Cleanup/test data lifecycle: create -> verify -> delete -> verify missing.
- Pytest yield fixture cleanup: setup -> yield -> teardown.
- Shared fixtures live in `tests/conftest.py` and are found by pytest automatically.
- Simple test configuration lives in `config.py`.
- Do not store secrets, passwords, or real tokens in `config.py`.
- `httpx.MockTransport` shows HTTP-like tests without real network calls.
- `tests/test_local_http_server.py` makes one real HTTP round trip to a temporary
  fake server on `127.0.0.1`; unlike `MockTransport`, it uses a local socket.
- HTTP client tests also check request details: method, path, and JSON body.
- HTTP tests show query params and basic headers.
- HTTP response tests show manual contract checks without extra libraries.
- HTTP response tests show JSON Schema validation with `jsonschema`.
- External API tests are skipped by default and run only when `RUN_EXTERNAL_API_TESTS=1`.
- HTTP auth tests show basic `Authorization: Bearer ...` header checks with a fake token.
- HTTP permission tests show user/admin access checks for a protected endpoint.
- Parametrized tests show an access-control matrix for the admin endpoint.
- Test organization uses `conftest.py` fixtures and reusable support helpers.

This is a learning example. It does not call a real API and does not use production framework patterns.
