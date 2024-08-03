import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import UserModel

from src.repository.users import (
    create_user, confirm_email, get_user_by_email,
    update_token, auto_response, delete_account
)

class TestUsersFunctions(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

    @patch('src.repository.users.User')
    async def test_create_user(self, mock_user):
        body = UserModel(
            username="testuser", email="test@example.com", password="password"
        )
        mock_user_instance = mock_user.return_value
        mock_user_instance.id = 2

        result = await create_user(body, self.session)

        mock_user.assert_called_once_with(**body.model_dump())
        self.session.add.assert_called_once_with(mock_user_instance)
        self.session.commit.assert_called_once()
        self.assertEqual(result, mock_user_instance)
        self.assertTrue(mock_user_instance.is_admin)

    @patch('src.repository.users.User')
    async def test_create_admin_user(self, mock_user):
        body = UserModel(
            username="admin", email="admin@example.com", password="adminpass"
        )
        mock_user_instance = mock_user.return_value
        mock_user_instance.id = 1

        result = await create_user(body, self.session)

        self.assertTrue(mock_user_instance.is_admin)

    async def test_confirm_email(self):
        mock_user = MagicMock()
        self.session.query().filter().first.return_value = mock_user

        await confirm_email("test@example.com", self.session)

        self.assertTrue(mock_user.confirmed)
        self.session.commit.assert_called_once()

    async def test_get_user_by_email(self):
        mock_user = MagicMock()
        self.session.query().filter().first.return_value = mock_user

        result = await get_user_by_email("test@example.com", self.session)

        self.assertEqual(result, mock_user)

    async def test_update_token(self):
        mock_user = MagicMock()
        token = "new_token"

        await update_token(mock_user, token, self.session)

        self.assertEqual(mock_user.refresh_token, token)
        self.session.commit.assert_called_once()

    async def test_auto_response(self):
        mock_user = MagicMock()
        response = True
        response_interval = 30

        await auto_response(
            response, response_interval, mock_user, self.session
        )

        self.assertEqual(mock_user.auto_response, response)
        self.assertEqual(mock_user.response_interval, response_interval)
        self.session.commit.assert_called_once()

    async def test_delete_account(self):
        mock_user = MagicMock()

        result = await delete_account(mock_user, self.session)

        self.session.delete.assert_called_once_with(mock_user)
        self.session.commit.assert_called_once()
        self.assertEqual(result, {'message': 'Account deleted'})

if __name__ == '__main__':
    unittest.main()
