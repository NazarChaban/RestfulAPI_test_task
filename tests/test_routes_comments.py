from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.database.models import User, Comment
from src.services.auth import auth_service
from main import app

client = TestClient(app)


def get_current_user_mock():
    return User(id=1, email="test@example.com", username="testuser")


@patch("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
@patch("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
@patch("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
class TestCommentsAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.dependency_overrides[auth_service.get_current_user] = get_current_user_mock

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides = {}

    def setUp(self):
        self.session_mock = MagicMock(spec=Session)

    @patch("src.repository.comments.create_comment")
    def test_create_comment(self, mock_create_comment):
        mock_create_comment.return_value = Comment(
            id=1, text="Test comment", user_id=1, post_id=1
        )

        response = client.post("/post-manager/comments/", json={
            "text": "Test comment",
            "post_id": 1
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["comment"]["text"], "Test comment")

    @patch("src.repository.comments.get_comments")
    def test_get_comments(self, mock_get_comments):
        mock_get_comments.return_value = [
            Comment(
                id=1, text="Test comment", created_at=datetime.now(),
                blocked=False, user_id=1, post_id=1
            )
        ]

        response = client.get("/post-manager/comments/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["text"], "Test comment")

    @patch("src.repository.comments.get_comment_by_id")
    def test_get_comment_by_id(self, mock_get_comment_by_id):
        mock_get_comment_by_id.return_value = Comment(
            id=1, text="Test comment", created_at=datetime.now(),
            blocked=False, user_id=1, post_id=1
        )

        response = client.get("/post-manager/comments/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["text"], "Test comment")

    @patch("src.repository.comments.get_comments_for_user")
    def test_get_comments_for_user(self, mock_get_comments_for_user):
        mock_get_comments_for_user.return_value = [
            Comment(
                id=1, text="Test comment", created_at=datetime.now(),
                blocked=False, user_id=1, post_id=1
            )
        ]

        response = client.get("/post-manager/comments/for-user/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["text"], "Test comment")

    @patch("src.repository.comments.get_comments_for_post")
    def test_get_comments_for_post(self, mock_get_comments_for_post):
        mock_get_comments_for_post.return_value = [
            Comment(
                id=1, text="Test comment", created_at=datetime.now(),
                blocked=False, user_id=1, post_id=1
            )
        ]

        response = client.get("/post-manager/comments/for-post/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["text"], "Test comment")

    @patch("src.repository.comments.get_comments_daily_breakdown")
    def test_get_comments_daily_breakdown(self, mock_get_comments_daily_breakdown):
        mock_get_comments_daily_breakdown.return_value = [
            {"date": "2023-08-03", "total_comments": 5, "blocked_comments": 1}
        ]

        response = client.get(
            "/post-manager/comments/daily-breakdown/1?date_from=2023-08-01&date_to=2023-08-03"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["total_comments"], 5)
        self.assertEqual(response.json()[0]["blocked_comments"], 1)

    @patch("src.repository.comments.update_comment")
    def test_update_comment(self, mock_update_comment):
        mock_comment = Comment(
            id=1, text="Updated comment", created_at=datetime.now(),
            blocked=False, user_id=1, post_id=1
        )

        mock_update_comment.return_value = {
            'comment': mock_comment, 'detail': 'Comment updated successfully'
        }

        response = client.patch(
            "/post-manager/comments/1", json={"text": "Updated comment"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["detail"], "Comment updated successfully"
        )

    @patch("src.repository.comments.delete_comment")
    def test_delete_comment(self, mock_delete_comment):
        mock_comment = Comment(
            id=1, text="Deleted comment", created_at=datetime.now(),
            blocked=False, user_id=1, post_id=1
        )
        mock_delete_comment.return_value = {
            'comment': mock_comment, 'detail': 'Comment deleted successfully'
        }

        response = client.delete("/post-manager/comments/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["detail"], "Comment deleted successfully"
        )

if __name__ == '__main__':
    unittest.main()
