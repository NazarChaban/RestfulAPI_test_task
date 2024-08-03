"""
This module contains the API routes for managing posts.

Routes:
- POST /posts: Create a new post.
- GET /posts: Get a list of posts based on the provided parameters.
- GET /posts/{post_id}: Get a post by its ID.
- GET /posts/{username}: Get a list of posts from a specific user.
- GET /posts/search: Search for posts based on text or author.
- PATCH /posts/{post_id}: Update a post by its ID.
- DELETE /posts/{post_id}: Delete a post by its ID.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.schemas import PostDB, PostResponse, PostBase
import src.repository.posts as repository_posts
from src.services.auth import auth_service
from src.database.models import User
from src.database.db import get_db

router = APIRouter(prefix='/posts', tags=['posts'])


@router.post(
    '/', response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def create_post(
    body: PostBase,
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The create_post function creates a new post in the database.

    :param body: The post data to create
    :param curr_user: The current user making the request
    :param db: The database session
    :return: The created post
    """
    post = await repository_posts.create_post(body, curr_user, db)
    return {'post': post, 'detail': 'Post created successfully'}


@router.get(
    '/', response_model=List[PostDB],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def get_posts(
    limit: int = Query(
        0, ge=0, description='Number of posts to return, 0 for all'
    ),
    offset: int = Query(
        0, ge=0, description='Number of posts to skip from start'
    ),
    descending: bool = Query(
        True,
        description='Sort posts in descending order, from newest to oldest'
    ),
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The get_posts function returns a list of posts based on the limit and
    offset provided. The posts can be sorted in ascending or descending order.

    :param limit: The number of posts to return
    :param offset: The number of posts to skip from the start
    :param descending: Sort the posts in descending order
    :param curr_user: The current user making the request
    :param db: The database session
    :return: A list of posts
    """
    return await repository_posts.get_posts(
        limit, offset, descending, db
    )


@router.get(
    '/search', response_model=List[PostDB],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def search_posts(
    text: Optional[str] = Query(None, description='Search by text'),
    author: Optional[str] = Query(None, description='Search by author'),
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The search_posts function searches for posts based on the text or author.

    :param text: The text to search for in posts
    :param author: The author to search for in posts
    :param db: The database session
    :return: A list of posts that match the search criteria
    """
    return await repository_posts.search_posts(text, author, db)


@router.get(
    '/{post_id}', response_model=PostDB,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def get_post_by_id(
    post_id: int,
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The get_post_by_id function returns a post by its ID.

    :param post_id: The ID of the post to return
    :param curr_user: The current user making the request
    :param db: The database session
    :return: The post with the specified ID
    """
    return await repository_posts.get_post_by_id(post_id, db)


@router.get(
    '/user/{username}', response_model=List[PostDB],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def get_posts_from_user(
    username: str,
    limit: int = Query(0, ge=0, description='Number of posts to return'),
    offset: int = Query(
        0, ge=0, description='Number of posts to skip from start'
    ),
    descending: bool = Query(
        True, description='Sort posts in descending order'
    ),
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The get_posts_from_user function returns a list of posts from a user.

    :param username: The username of the user to get posts from
    :param limit: The number of posts to return
    :param offset: The number of posts to skip from the start
    :param descending: Sort the posts in descending order
    :param db: The database session
    :return: A list of posts from the specified user
    """
    return await repository_posts.get_posts_from_user(
        username, limit, offset, descending, db
    )


@router.patch(
    '/{post_id}', response_model=PostDB,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def update_post(
    post_id: int,
    body: PostBase,
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The update_post function updates a post by its ID.

    :param post_id: The ID of the post to update
    :param body: The post data to update
    :param curr_user: The current user making the request
    :param db: The database session
    :return: The updated post
    """
    return await repository_posts.update_post(post_id, body, curr_user, db)


@router.delete(
    '/{post_id}', status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def delete_post(
    post_id: int,
    curr_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The delete_post function deletes a post by its ID.

    :param post_id: The ID of the post to delete
    :param curr_user: The current user making the request
    :param db: The database session
    :return: None
    """
    return await repository_posts.delete_post(post_id, curr_user, db)
