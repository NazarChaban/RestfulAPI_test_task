"""
The users module contains functions that interact with the database.
"""
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def create_user(
    body: UserModel,
    db: Session
) -> User:
    """
    The create_user function creates a new user in the database.

    :param body: Get the data from the request body
    :param db: Pass the database session to the repository
    :return: User
    """
    new_user = User(**body.model_dump())
    if new_user.id == 1:
        new_user.is_admin = True
    db.add(new_user)
    db.commit()
    return new_user


async def confirm_email(
    email: str,
    db: Session
) -> None:
    """
    The confirm_email function confirms the email of a user.

    :param email: Get the email of the user
    :param db: Pass the database session to the repository
    :return: None
    """
    user = db.query(User).filter(User.email == email).first()
    user.confirmed = True
    db.commit()


async def get_user_by_email(
    email: str,
    db: Session
) -> User:
    """
    The get_user_by_email function retrieves a user from the database by email.

    :param email: Get the email of the user
    :param db: Pass the database session to the repository
    :return: User
    """
    return db.query(User).filter(User.email == email).first()


async def update_token(
    user: User,
    token: str | None,
    db: Session
) -> None:
    """
    The update_token function updates the refresh token of a user.

    :param user: Get the user object
    :param token: Get the refresh token
    :param db: Pass the database session to the repository
    :return: None
    """
    user.refresh_token = token
    db.commit()


async def auto_response(
    response: bool,
    response_interval: int,
    user: User,
    db: Session
):
    """
    The auto_response function changes the auto_response parameter of a user.
    If True AI will automatically respond to comments.

    :param user: Get the current user
    :param db: Get the database session
    :return: The current user
    """
    user.auto_response = response
    user.response_interval = response_interval
    db.commit()


async def delete_account(
    user: User,
    db: Session
) -> dict:
    """
    The delete_account function deletes the current user's account.

    :param user: Get the current user
    :param db: Get the database session
    :return: Message {'message': 'Account deleted'}
    """
    db.delete(user)
    db.commit()
    return {'message': 'Account deleted'}
