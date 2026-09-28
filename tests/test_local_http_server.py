from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import httpx
import pytest

from clients.http_users_client import HttpUsersClient


@pytest.fixture
def local_http_users_client():
    received_requests = []

    class FakeUsersHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            received_requests.append((self.command, self.path))
            body = b'{"id": 1, "name": "Egor", "email": "egor@example.com"}'

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeUsersHandler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()

    try:
        with httpx.Client(
            base_url=f"http://127.0.0.1:{server.server_port}",
            trust_env=False,
        ) as http_client:
            yield HttpUsersClient(http_client), received_requests
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join()


@pytest.mark.api
def test_get_user_over_local_http(local_http_users_client):
    client, received_requests = local_http_users_client

    response = client.get_user(1)

    assert received_requests == [("GET", "/users/1")]
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Egor",
        "email": "egor@example.com",
    }
