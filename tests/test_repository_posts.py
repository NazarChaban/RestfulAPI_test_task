import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.database.models import User, Post
from src.schemas import PostBase, PostAiModel
from src.repository.posts import (
    get_posts, create_post, get_post_by_id, update_post,
    delete_post, get_posts_from_user, search_posts
)

class TestPostsFunctions(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = MagicMock(spec=User)
        self.user.id = 1

    @patch('src.repository.posts.Post')
    async def test_get_posts(self, mock_post):
        mock_query = self.session.query.return_value
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [MagicMock(spec=Post)]

        result = await get_posts(limit=10, offset=0, descending=True, db=self.session)

        self.assertEqual(len(result), 1)
        mock_query.order_by.assert_called_once()
        mock_query.order_by.return_value.offset.assert_called_once_with(0)
        mock_query.order_by.return_value.offset.return_value.limit.assert_called_once_with(10)

    @patch('src.repository.posts.Post')
    @patch('src.repository.posts.moderate_content')
    async def test_create_post(self, mock_moderate, mock_post):
        body = PostBase(text="Test post")
        mock_post.return_value = MagicMock(spec=Post)
        mock_moderate.return_value = {'is_acceptable': True}

        result = await create_post(body, self.user, self.session)

        mock_post.assert_called_once_with(text="Test post", created_at=unittest.mock.ANY, user_id=self.user.id)
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertIsInstance(result, MagicMock)

    async def test_get_post_by_id(self):
        mock_post = MagicMock(spec=Post)
        self.session.query.return_value.filter.return_value.first.return_value = mock_post

        result = await get_post_by_id(post_id=1, db=self.session)

        self.assertEqual(result, mock_post)

    async def test_update_post(self):
        body = PostBase(text="Updated post")
        mock_post = MagicMock(spec=Post)
        self.session.query.return_value.filter.return_value.first.return_value = mock_post

        result = await update_post(
            post_id=1, body=body, user=self.user, db=self.session
        )

        self.session.commit.assert_called_once()

    async def test_delete_post(self):
        mock_post = MagicMock(spec=Post)
        self.session.query.return_value.filter.return_value.first.return_value = mock_post

        result = await delete_post(post_id=1, user=self.user, db=self.session)

        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertEqual(result, {'detail': 'Post deleted successfully'})

    @patch('src.repository.posts.Post')
    async def test_get_posts_from_user(self, mock_post):
        mock_query = self.session.query.return_value
        mock_query.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [MagicMock(spec=Post)]

        result = await get_posts_from_user(username="testuser", limit=10, offset=0, descending=True, db=self.session)

        self.assertEqual(len(result), 1)
        mock_query.filter.assert_called_once()
        mock_query.filter.return_value.order_by.assert_called_once()
        mock_query.filter.return_value.order_by.return_value.offset.assert_called_once_with(0)
        mock_query.filter.return_value.order_by.return_value.offset.return_value.limit.assert_called_once_with(10)

    @patch('src.repository.posts.Post')
    async def test_search_posts(self, mock_post):
        mock_query = self.session.query.return_value
        mock_query.filter.return_value.all.return_value = [MagicMock(spec=Post)]

        result = await search_posts(text="test", author=None, db=self.session)

        self.assertEqual(len(result), 1)
        mock_query.filter.assert_called_once()

if __name__ == '__main__':
    unittest.main()
