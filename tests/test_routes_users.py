from unittest.mock import patch, MagicMock, AsyncMock
import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.schemas import PostBase, PostDB, UserDB
from src.database.models import User
from main import app


@patch("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
@patch("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
@patch("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
class TestUserRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_user = User(
            id=1, username="testuser", email="test@example.com"
        )

    @patch("src.services.auth.auth_service.get_current_user")
    def test_get_me(self, mock_get_current_user):
        mock_get_current_user.return_value = self.test_user
        response = self.client.get("/post-manager/users/me")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "testuser")
        self.assertEqual(response.json()["email"], "test@example.com")

    @patch("src.services.auth.auth_service.get_current_user")
    @patch("src.database.db.get_db")
    def test_auto_response_enable(self, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.test_user
        mock_db = MagicMock(spec=Session)
        mock_get_db.return_value = mock_db

        with patch("src.repository.users.auto_response") as mock_auto_response:
            mock_auto_response.return_value = {
                "message": "Auto response enabled successfully"
            }
            response = self.client.post(
                "/post-manager/users/auto-response?auto_response=True&response_interval=300"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"message": "Auto response enabled successfully"}
        )

    @patch("src.services.auth.auth_service.get_current_user")
    @patch("src.database.db.get_db")
    def test_auto_response_disable(self, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.test_user
        mock_db = MagicMock(spec=Session)
        mock_get_db.return_value = mock_db

        with patch("src.repository.users.auto_response") as mock_auto_response:
            mock_auto_response.return_value = {
                "message": "Auto response disabled successfully"
            }
            response = self.client.post(
                "/post-manager/users/auto-response?response=false"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"message": "Auto response disabled successfully"}
        )

    @patch("src.services.auth.auth_service.get_current_user")
    @patch("src.database.db.get_db")
    def test_delete_account(self, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.test_user
        mock_db = MagicMock(spec=Session)
        mock_get_db.return_value = mock_db

        with patch("src.repository.users.delete_account") as mock_delete_account:
            mock_delete_account.return_value = {
                "message": "Account deleted successfully"
            }
            response = self.client.delete("/post-manager/users/me/delete")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"message": "Account deleted successfully"}
        )

if __name__ == '__main__':
    unittest.main()
