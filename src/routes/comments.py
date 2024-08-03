"""
This module contains the API routes for managing comments.

Endpoints:
- POST /comments: Create a new comment for a post.
- GET /comments: Get all comments from the current user.
- GET /comments/{comment_id}: Get a comment by its ID.
- GET /comments/for-user/{user_id}: Get all comments for a user.
- GET /comments/for-post/{post_id}: Get all comments for a post.
- GET /comments/daily-breakdown/{post_id}: Get statistic based on blocked and not blocked comments for a post within a date range.
- PATCH /comments/{comment_id}: Update a comment.
- DELETE /comments/{comment_id}: Delete a comment.
"""
from typing import List
from fastapi import APIRouter, Depends, status, Query
from fastapi_limiter.depends import RateLimiter
from fastapi.background import BackgroundTasks
from sqlalchemy.orm import Session

from src.schemas import (
    CommentBase, CommentCreate, CommentDB, CommentResponse,
    CommentDailyBreakdown
)
import src.repository.comments as repository_comments
from src.services.auth import auth_service
from src.database.models import User
from src.database.db import get_db

router = APIRouter(prefix='/comments', tags=['comments'])


@router.post(
    '/', response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def create_comment(
    body: CommentCreate,
    background_tasks: BackgroundTasks,
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The create_comment function creates a new comment for a post.

    :param body: The comment data
    :param db: The database session
    :return: The created comment
    """
    return await repository_comments.create_comment(
        body, curr_user, db, background_tasks
    )


@router.get(
    '/', response_model=List[CommentDB],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def get_comments(
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The get_comments function return all comments from current user.

    :param curr_user: The current user
    :param db: The database session
    :return: The list of comments
    """
    return await repository_comments.get_comments(curr_user, db)


@router.get(
    '/{comment_id}', response_model=CommentDB,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def get_comment_by_id(
    comment_id: int,
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The get_comment_by_id function return a comment by id.

    :param comment_id: The comment id
    :param db: The database session
    :return: The comment
    """
    return await repository_comments.get_comment_by_id(
        comment_id, curr_user, db
    )


@router.get(
    '/for-user/{user_id}', response_model=List[CommentDB],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def get_comments_for_user(
    user_id: int,
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The get_comments_for_user function return all comments for a user.

    :param user_id: The user id
    :param db: The database session
    :return: The list of comments
    """
    return await repository_comments.get_comments_for_user(
        user_id, curr_user, db
    )


@router.get(
    '/for-post/{post_id}', response_model=List[CommentDB],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def get_comments_for_post(
    post_id: int,
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The get_comments_for_post function return all comments for a post.

    :param post_id: The post id
    :param db: The database session
    :return: The list of comments
    """
    return await repository_comments.get_comments_for_post(
        post_id, curr_user, db
    )


@router.get(
    '/daily-breakdown/{post_id}', response_model=List[CommentDailyBreakdown],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def get_comments_daily_breakdown(
    post_id: int,
    date_from: str = Query(None, description='The start date'),
    date_to: str = Query(None, description='The end date'),
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The get_comments_daily_breakdown function return all comments for a post
    within a date range.
    It will return analytics aggregated by day, for each day, the number of
    comments created and the number of comments blocked

    :param post_id: The post id
    :param date_from: The start date
    :param date_to: The end date
    :param db: The database session
    :return: The list of comments
    """
    return await repository_comments.get_comments_daily_breakdown(
        post_id, date_from, date_to, curr_user, db
    )


@router.patch(
    '/{comment_id}', response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def update_comment(
    comment_id: int,
    body: CommentBase,
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The update_comment function updates a comment.

    :param comment_id: The comment id
    :param body: The comment data
    :param curr_user: The current user
    :param db: The database session
    :return: The updated comment
    """
    return await repository_comments.update_comment(
        comment_id, body, curr_user, db
    )


@router.delete(
    '/{comment_id}', response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def delete_comment(
    comment_id: int,
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The delete_comment function deletes a comment.

    :param comment_id: The comment id
    :param curr_user: The current user
    :param db: The database session
    :return: The deleted comment
    """
    return await repository_comments.delete_comment(comment_id, curr_user, db)
