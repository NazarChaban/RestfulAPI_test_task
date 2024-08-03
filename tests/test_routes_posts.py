from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.schemas import PostBase, PostDB, UserDB
from src.database.models import User, Post
from main import app


@patch("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
@patch("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
@patch("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
class TestPostRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_user = User(id=1, username="testuser")
        self.test_post = Post(id=1, text="Test Post", user_id=1)

    @patch("src.services.auth.auth_service.get_current_user")
    @patch("src.database.db.get_db")
    def test_create_post(self, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.test_user
        mock_db = MagicMock(spec=Session)
        mock_get_db.return_value = mock_db

        with patch("src.repository.posts.create_post") as mock_create_post:
            mock_create_post.return_value = self.test_post
            response = self.client.post(
                "/post-manager/posts/", json={"text": "Test Post"}
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["post"]["text"], "Test Post")

    @patch("src.services.auth.auth_service.get_current_user")
    @patch("src.database.db.get_db")
    def test_get_posts(self, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.test_user
        mock_db = MagicMock(spec=Session)
        mock_get_db.return_value = mock_db

        with patch("src.repository.posts.get_posts") as mock_get_posts:
            mock_get_posts.return_value = [self.test_post]
            response = self.client.get("/post-manager/posts/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["text"], "Test Post")

    @patch("src.services.auth.auth_service.get_current_user")
    @patch("src.database.db.get_db")
    def test_search_posts(self, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.test_user
        mock_db = MagicMock(spec=Session)
        mock_get_db.return_value = mock_db

        with patch("src.repository.posts.search_posts") as mock_search_posts:
            mock_search_posts.return_value = [self.test_post]
            response = self.client.get(
                "/post-manager/posts/search?text=test&author=testuser"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["text"], "Test Post")

    @patch("src.services.auth.auth_service.get_current_user")
    @patch("src.database.db.get_db")
    def test_get_post_by_id(self, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.test_user
        mock_db = MagicMock(spec=Session)
        mock_get_db.return_value = mock_db

        with patch("src.repository.posts.get_post_by_id") as mock_get_post_by_id:
            mock_get_post_by_id.return_value = self.test_post
            response = self.client.get("/post-manager/posts/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["text"], "Test Post")

    @patch("src.services.auth.auth_service.get_current_user")
    @patch("src.database.db.get_db")
    def test_get_posts_from_user(self, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.test_user
        mock_db = MagicMock(spec=Session)
        mock_get_db.return_value = mock_db

        with patch("src.repository.posts.get_posts_from_user") as mock_get_posts_from_user:
            mock_get_posts_from_user.return_value = [self.test_post]
            response = self.client.get("/post-manager/posts/user/testuser")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["text"], "Test Post")

    @patch("src.services.auth.auth_service.get_current_user")
    @patch("src.database.db.get_db")
    def test_update_post(self, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.test_user
        mock_db = MagicMock(spec=Session)
        mock_get_db.return_value = mock_db

        updated_post = Post(
            id=1, text="Updated Post", created_at=datetime.now(), user_id=1
        )
        with patch("src.repository.posts.update_post") as mock_update_post:
            mock_update_post.return_value = updated_post
            response = self.client.patch(
                "/post-manager/posts/1", json={"text": "Updated Post"}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["text"], "Updated Post")

    @patch("src.services.auth.auth_service.get_current_user")
    @patch("src.database.db.get_db")
    def test_delete_post(self, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.test_user
        mock_db = MagicMock(spec=Session)
        mock_get_db.return_value = mock_db

        with patch("src.repository.posts.delete_post") as mock_delete_post:
            mock_delete_post.return_value = {
                "message": "Post deleted successfully"
            }
            response = self.client.delete("/post-manager/posts/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"message": "Post deleted successfully"}
        )


if __name__ == '__main__':
    unittest.main()
