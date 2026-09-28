class HttpUsersClient:
    def __init__(self, http_client):
        self.http_client = http_client

    def get_user(self, user_id):
        return self.http_client.get(f"/users/{user_id}")

    def get_current_user(self):
        return self.http_client.get("/me")

    def get_admin_users(self):
        return self.http_client.get("/admin/users")

    def search_users(self, email=None, limit=None):
        params = {}

        if email:
            params["email"] = email

        if limit:
            params["limit"] = limit

        return self.http_client.get("/users", params=params)

    def create_user(self, user_data):
        return self.http_client.post("/users", json=user_data)

    def delete_user(self, user_id):
        return self.http_client.delete(f"/users/{user_id}")
