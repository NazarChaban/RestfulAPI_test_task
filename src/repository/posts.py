"""
This module contains functions for interacting with the posts table in the database.
"""
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.services.ai_services import moderate_content
from src.schemas import PostBase, PostAiModel
from src.database.models import User, Post

AI_MODERATION = True


async def get_posts(
    limit: int,
    offset : int,
    descending: bool,
    db: Session
) -> list[Post]:
    """
    The get_posts function returns a list of posts based on the limit and
    offset provided. The posts can be sorted in ascending or descending order.

    :param limit: The number of posts to return
    :param offset: The number of posts to skip from the start
    :param descending: Sort the posts in descending order
    :param db: The database session
    :return: A list of posts
    """
    order_seq = Post.created_at.desc() if descending else Post.created_at.asc()
    query = db.query(Post).order_by(order_seq).offset(offset)
    if limit > 0:
        query = query.limit(limit)
    return query.all()


async def create_post(
    body: PostBase,
    user: User,
    db: Session
) -> Post:
    """
    The create_post function creates a new post in the database.

    :param body: The post data to create
    :param user: The user creating the post
    :param db: The database session
    :return: The created post
    """
    post = Post(
        text=body.text,
        created_at = datetime.now().strftime('%Y-%m-%d'),
        user_id=user.id
    )

    if AI_MODERATION:
        moderation = await moderate_content(PostAiModel(
            post_text=post.text
        ))
        if not moderation['is_acceptable']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=moderation['explanation']
            )

    db.add(post)
    db.commit()
    return post


async def get_post_by_id(
    post_id: int,
    db: Session,
    user: User = None
) -> Post:
    """
    The get_post_by_id function returns a post based on the post_id and user_id.
    Parameter user is optional and is used to check if the post belongs to the user if function is called from update_post or delete_post.

    :param post_id: The ID of the post to return
    :param user: The user making the request
    :param db: The database session
    :return: The post with the specified ID
    """
    query = db.query(Post).filter(Post.id == post_id)
    if user is not None:
        query = query.filter(Post.user_id == user.id)
    return query.first()


async def update_post(
    post_id: int,
    body: PostBase,
    user: User,
    db: Session
) -> Post:
    """
    The update_post function updates a post based on the post_id and user_id.

    :param post_id: The ID of the post to update
    :param body: The post data to update
    :param user: The user making the request
    :param db: The database session
    :return: The updated post
    """
    post = await get_post_by_id(post_id, db, user)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post not found'
        )
    post.text = body.text
    db.commit()
    return post


async def delete_post(
    post_id: int,
    user: User,
    db: Session
) -> dict:
    """
    The delete_post function deletes a post based on the post_id and user_id.

    :param post_id: The ID of the post to delete
    :param user: The user making the request
    :param db: The database session
    :return: A message indicating the success of the operation
    """
    post = await get_post_by_id(post_id, db, user)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post not found'
        )
    db.delete(post)
    db.commit()
    return {'detail': 'Post deleted successfully'}


async def get_posts_from_user(
    username: str,
    limit: int,
    offset: int,
    descending: bool,
    db: Session
) -> list[Post]:
    """
    The get_posts_from_user function returns a list of posts from a user.

    :param username: The username of the user to get posts from
    :param limit: The number of posts to return
    :param offset: The number of posts to skip from the start
    :param descending: Sort the posts in descending order
    :param db: The database session
    :return: A list of posts from the specified user
    """
    order_seq = Post.created_at.desc() if descending else Post.created_at.asc()
    query = db.query(Post).filter(
        Post.user.has(username=username)
    ).order_by(order_seq).offset(offset)
    if limit > 0:
        query = query.limit(limit)
    return query.all()


async def search_posts(
    text: Optional[str],
    author: Optional[str],
    db: Session
) -> list[Post]:
    """
    The search_posts function searches for posts based on the text or author.
    If both text and author are provided, the search is performed on both fields.

    :param text: Search by text
    :param author: Search by author
    :param db: The database session
    :return: A list of posts matching the search criteria
    """
    query = db.query(Post)
    if text and author:
        query = query.filter(and_(
            Post.text.ilike(f"%{text}%"), Post.user.has(username=author)
        ))
    elif text:
        query = query.filter(Post.text.ilike(f"%{text}%"))
    elif author:
        query = query.filter(Post.user.has(username=author))

    return query.all()
