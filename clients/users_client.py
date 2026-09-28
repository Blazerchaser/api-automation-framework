from config import DEFAULT_USER


class UsersClient:
    def __init__(self):
        self.users = {
            DEFAULT_USER["id"]: dict(DEFAULT_USER),
        }

    def get_user(self, user_id):
        user = self.users.get(user_id)

        if user is None:
            return {
                "status_code": 404,
                "json": {
                    "error": "Not Found",
                    "message": "User not found",
                },
            }

        return {
            "status_code": 200,
            "json": user,
        }

    def create_user(self, user_data):
        if not user_data or "name" not in user_data or "email" not in user_data:
            return {
                "status_code": 400,
                "json": {
                    "error": "Bad Request",
                    "message": "Name and email are required",
                },
            }

        new_id = max(self.users) + 1
        created_user = {
            "id": new_id,
            "name": user_data["name"],
            "email": user_data["email"],
        }
        self.users[new_id] = created_user

        return {
            "status_code": 201,
            "json": created_user,
        }

    def delete_user(self, user_id):
        if user_id not in self.users:
            return {
                "status_code": 404,
                "json": {
                    "error": "Not Found",
                    "message": "User not found",
                },
            }

        del self.users[user_id]

        return {
            "status_code": 204,
            "json": None,
        }
