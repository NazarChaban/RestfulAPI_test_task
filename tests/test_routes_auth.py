from unittest.mock import patch, MagicMock, AsyncMock
import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.services.auth import auth_service
from src.database.models import User
from main import app

client = TestClient(app)


@patch("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
@patch("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
@patch("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
class TestAuthAPI(unittest.TestCase):

    def setUp(self):
        self.session_mock = MagicMock(spec=Session)

    @patch("src.repository.users.get_user_by_email")
    @patch("src.repository.users.create_user")
    @patch("src.services.auth.auth_service.get_password_hash")
    def test_signup(
        self, mock_get_password_hash, mock_create_user, mock_get_user_by_email
    ):
        mock_get_user_by_email.return_value = None
        mock_get_password_hash.return_value = "hashed_password"
        mock_create_user.return_value = User(
            id=1, email="new@example.com", username="newuser"
        )

        response = client.post("/post-manager/auth/signup", json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "password123"
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user"]["email"], "new@example.com")

    @patch("src.repository.users.get_user_by_email")
    @patch("src.services.auth.auth_service.verify_password")
    @patch("src.services.auth.auth_service.create_access_token")
    @patch("src.services.auth.auth_service.create_refresh_token")
    @patch("src.repository.users.update_token")
    def test_login(
        self, mock_update_token, mock_create_refresh_token,
        mock_create_access_token, mock_verify_password, mock_get_user_by_email
    ):
        mock_get_user_by_email.return_value = User(
            id=1, email="test@example.com", username="testuser", confirmed=True
        )
        mock_verify_password.return_value = True
        mock_create_access_token.return_value = "access_token"
        mock_create_refresh_token.return_value = "refresh_token"

        response = client.post("/post-manager/auth/login", data={
            "username": "test@example.com",
            "password": "password123"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["access_token"], "access_token")
        self.assertEqual(response.json()["refresh_token"], "refresh_token")

    @patch("src.services.auth.auth_service.decode_refresh_token")
    @patch("src.repository.users.get_user_by_email")
    @patch("src.services.auth.auth_service.create_access_token")
    @patch("src.services.auth.auth_service.create_refresh_token")
    @patch("src.repository.users.update_token")
    def test_refresh_token(
        self, mock_update_token, mock_create_refresh_token,
        mock_create_access_token, mock_get_user_by_email,
        mock_decode_refresh_token
    ):
        mock_decode_refresh_token.return_value = "test@example.com"
        mock_get_user_by_email.return_value = User(
            id=1, email="test@example.com", username="testuser", refresh_token="old_refresh_token"
        )
        mock_create_access_token.return_value = "new_access_token"
        mock_create_refresh_token.return_value = "new_refresh_token"

        response = client.get(
            "/post-manager/auth/refresh-token",
            headers={"Authorization": "Bearer old_refresh_token"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["access_token"], "new_access_token")
        self.assertEqual(response.json()["refresh_token"], "new_refresh_token")

    @patch("src.services.auth.auth_service.get_email_from_token")
    @patch("src.repository.users.get_user_by_email")
    @patch("src.repository.users.confirm_email")
    def test_confirm_email(
        self, mock_confirm_email, mock_get_user_by_email,
        mock_get_email_from_token
    ):
        mock_get_email_from_token.return_value = "test@example.com"
        mock_get_user_by_email.return_value = User(
            id=1, email="test@example.com",
            username="testuser", confirmed=False
        )

        response = client.get("/post-manager/auth/confirm-email/some_token")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Email confirmed")

    @patch("src.repository.users.get_user_by_email")
    def test_request_email(self, mock_get_user_by_email):
        mock_get_user_by_email.return_value = User(
            id=1, email="test@example.com",
            username="testuser", confirmed=False
        )

        response = client.post(
            "/post-manager/auth/request-email",
            json={"email": "test@example.com"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["message"], "Check your email for confirmation"
        )

if __name__ == '__main__':
    unittest.main()
