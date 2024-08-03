import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks

from src.database.models import User, Post, Comment
from src.schemas import CommentBase, CommentCreate, CommentAiModel
from src.repository.comments import (
    create_comment, get_comments, get_comment_by_id, get_comments_for_user,
    get_comments_for_post, get_comments_daily_breakdown, update_comment, delete_comment
)

class TestCommentsFunctions(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = MagicMock(spec=User)
        self.user.id = 1
        self.post = MagicMock(spec=Post)
        self.post.id = 1
        self.background_tasks = MagicMock(spec=BackgroundTasks)

    @patch('src.repository.comments.Comment')
    @patch('src.repository.comments.moderate_content')
    @patch('src.repository.comments.comment_pool.add_comment')
    async def test_create_comment(self, mock_add_comment, mock_moderate, mock_comment):
        body = CommentCreate(
            text="Test comment", response_on_comment=0, post_id=1
        )
        mock_comment.return_value = MagicMock(spec=Comment)
        mock_moderate.return_value = {'is_acceptable': True}
        self.session.query().filter().first.return_value = self.post

        result = await create_comment(
            body, self.user, self.session, self.background_tasks
        )

        mock_comment.assert_called_once_with(
            text="Test comment", response_on_comment=None, post_id=1,
            created_at=unittest.mock.ANY, user_id=self.user.id
        )
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertIsInstance(result['comment'], MagicMock)
        self.assertEqual(result['detail'], 'Comment created successfully')

    async def test_get_comments(self):
        mock_comments = [MagicMock(spec=Comment) for _ in range(3)]
        self.session.query().filter().all.return_value = mock_comments

        result = await get_comments(self.user, self.session)

        self.assertEqual(len(result), 3)

    async def test_get_comment_by_id(self):
        mock_comment = MagicMock(spec=Comment)
        self.session.query().filter().first.return_value = mock_comment

        result = await get_comment_by_id(
            comment_id=1, user=self.user, db=self.session
        )

        self.assertEqual(result, mock_comment)

    async def test_get_comments_for_user(self):
        mock_comments = [MagicMock(spec=Comment) for _ in range(3)]
        self.session.query(
        ).filter.return_value.all.return_value = mock_comments

        result = await get_comments_for_user(
            user_id=1, user=self.user, db=self.session
        )

        self.assertEqual(len(result), 3)
        self.session.query().filter.assert_called_once()

    async def test_get_comments_for_post(self):
        mock_comments = [MagicMock(spec=Comment) for _ in range(3)]
        self.session.query().filter().all.return_value = mock_comments
        self.session.query().filter().first.return_value = self.post

        result = await get_comments_for_post(
            post_id=1, user=self.user, db=self.session
        )

        self.assertEqual(len(result), 3)
        self.session.query().filter.assert_called()

    @patch('src.repository.comments.datetime')
    async def test_get_comments_daily_breakdown(self, mock_datetime):
        mock_datetime.strptime.side_effect = lambda date, format: datetime.strptime(date, format)
        mock_comments = [
            MagicMock(
                spec=Comment, created_at=datetime(2023, 1, 1), blocked=False
            ),
            MagicMock(
                spec=Comment, created_at=datetime(2023, 1, 1), blocked=True
            ),
            MagicMock(
                spec=Comment, created_at=datetime(2023, 1, 2), blocked=False
            ),
        ]
        self.session.query().filter().all.return_value = mock_comments
        self.session.query().filter().first.return_value = self.post

        result = await get_comments_daily_breakdown(
            post_id=1, date_from="2023-01-01", date_to="2023-01-02",
            user=self.user, db=self.session
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['total_comments'], 2)
        self.assertEqual(result[0]['blocked_comments'], 1)
        self.assertEqual(result[1]['total_comments'], 1)
        self.assertEqual(result[1]['blocked_comments'], 0)

    async def test_update_comment(self):
        body = CommentBase(text="Updated comment")
        mock_comment = MagicMock(spec=Comment)
        self.session.query().filter().first.return_value = mock_comment

        result = await update_comment(
            comment_id=1, body=body, user=self.user, db=self.session
        )

        self.assertEqual(mock_comment.text, "Updated comment")
        self.session.commit.assert_called_once()
        self.assertEqual(result['comment'], mock_comment)
        self.assertEqual(result['detail'], 'Comment updated successfully')

    async def test_delete_comment(self):
        mock_comment = MagicMock(spec=Comment)
        self.session.query().filter().first.return_value = mock_comment

        result = await delete_comment(
            comment_id=1, user=self.user, db=self.session
        )

        self.session.delete.assert_called_once_with(mock_comment)
        self.session.commit.assert_called_once()
        self.assertEqual(result['comment'], mock_comment)
        self.assertEqual(result['detail'], 'Comment deleted successfully')

if __name__ == '__main__':
    unittest.main()
