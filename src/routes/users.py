"""
This module contains the API routes related to user operations.

It defines the following routes:
- GET /users/me: Returns the current user's information.
- POST /users/auto-response: Sets the auto response status for the current user.
- DELETE /users/me/delete: Deletes the current user's account.
"""
from fastapi import APIRouter, Depends, status, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

import src.repository.users as repository_users
from src.services.auth import auth_service
from src.database.models import User
from src.conf.config import settings
from src.database.db import get_db
from src.schemas import UserDB

router = APIRouter(prefix='/users', tags=['users'])


@router.get(
    '/me', response_model=UserDB,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def get_me(
    curr_user: User = Depends(auth_service.get_current_user)
):
    """
    The read_users_me function returns the current user's information.

    :param curr_user: Get the current user
    :return: The current user
    """
    return curr_user


@router.post(
    '/auto-response',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def auto_response(
    response: bool = Query(
        default=False, description='Auto response status. True or False'
    ),
    response_interval: int = Query(
        default=300, description='Response interval in seconds'
    ),
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The auto_response function returns the current user's information.

    :param curr_user: Get the current user
    :param db: Get the database session
    :return: The current user
    """
    return await repository_users.auto_response(
        response, response_interval, curr_user, db
    )


@router.delete(
    '/me/delete',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def delete_account(
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The delete_account function deletes the current user's account.

    :param curr_user: Get the current user
    :param db: Get the database session
    :return: None
    """
    return await repository_users.delete_account(curr_user, db)
