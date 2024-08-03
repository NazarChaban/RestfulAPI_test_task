"""
The comments module contains functions to interact with the comments table in the database.
"""
from datetime import datetime
from fastapi.background import BackgroundTasks
from sqlalchemy import and_, func, Integer
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import Comment, User, Post
from src.schemas import CommentBase, CommentCreate, CommentAiModel
from src.services.ai_services import (
    moderate_content, comment_response, comment_pool
)

AI_MODERATION = True
AI_RESPONSE = True


async def create_comment(
    body: CommentCreate,
    user: User,
    db: Session,
    background_tasks: BackgroundTasks
) -> Comment:
    """
    The create_comment function creates a new comment for a post.

    :param body: The comment data
    :param db: The database session
    :return: The created comment
    """
    body.response_on_comment = body.response_on_comment or None
    comment = Comment(
        **body.model_dump(),
        created_at = datetime.now().strftime('%Y-%m-%d'),
        user_id=user.id
    )
    post = db.query(Post).filter(Post.id == body.post_id).first()

    if AI_MODERATION:
        moderation = await moderate_content(CommentAiModel(
            post_text=post.text,
            comment_text=comment.text
        ))
        if not moderation['is_acceptable']:
            comment.blocked = True
            comment.block_reason = moderation['explanation']

    if AI_RESPONSE:
        post_author = db.query(User).filter(User.id == post.user_id).first()
        if post_author.auto_response and not comment.blocked:
            background_tasks.add_task(
                comment_pool.add_comment, comment, post,
                post_author.response_interval, comment_response
            )

    db.add(comment)
    db.commit()
    return {'comment': comment, 'detail': 'Comment created successfully'}


async def get_comments(
    user: User,
    db: Session
) -> list[Comment]:
    """
    The get_comments function return all comments from current user.

    :param user: The current user
    :param db: The database session
    :return: The list of comments
    """
    return db.query(Comment).filter(Comment.user_id == user.id).all()


async def get_comment_by_id(
    comment_id: int,
    user: User,
    db: Session
) -> Comment:
    """
    The get_comment_by_id function return a comment by its id.
    And if the user is not an admin, it will return only the comments that are not blocked.

    :param comment_id: The comment id
    :param user: The current user
    :param db: The database session
    :return: The comment
    """
    query = db.query(Comment).filter(Comment.id == comment_id)
    if not user.is_admin:
        query = query.filter(Comment.blocked == False)
    return query.first()


async def get_comments_for_user(
    user_id: int,
    user: User,
    db: Session
) -> list[Comment]:
    """
    The get_comments_for_user function return all comments from a user.
    And if the user is not an admin or an author, it will return only the comments that are not blocked.

    :param user_id: The user id
    :param user: The current user
    :param db: The database session
    :return: The list of comments
    """
    is_author = user.id == user_id
    query =  db.query(Comment).filter(Comment.user_id == user_id)
    if not user.is_admin and not is_author:
        query = query.filter(Comment.blocked == False)
    return query.all()


async def get_comments_for_post(
    post_id: int,
    user: User,
    db: Session
) -> list[Comment]:
    """
    The get_comments_for_post function return all comments for a post.
    And if the user is not an admin or an author, it will return only the comments that are not blocked.

    :param post_id: The post id
    :param user: The current user
    :param db: The database session
    :return: The list of comments
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    is_author = post.user_id == user.id
    query = db.query(Comment).filter(Comment.post_id == post_id)

    if not user.is_admin and not is_author:
        query = query.filter(Comment.blocked == False)
    return query.all()


async def get_comments_daily_breakdown(
    post_id: int,
    date_from: str,
    date_to: str,
    user: User,
    db: Session
):
    """
    The get_comments_daily_breakdown function will return analytics aggregated
    by day for each day. It will return the number of comments created and the
    number of comments blocked.
    If the user is not the author or admin, the function will return an exception

    :param post_id: The post id
    :param date_from: The start date
    :param date_to: The end date
    :param db: The database session
    :return: The list of comments
    """
    date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
    date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
    post = db.query(Post).filter(Post.id == post_id).first()
    is_author = post.user_id == user.id

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    if not user.is_admin and not is_author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    comments = db.query(Comment).filter(and_(
        Comment.post_id == post_id,
        Comment.created_at >= date_from_dt,
        Comment.created_at <= date_to_dt
    )).all()

    results = {}
    for comment in comments:
        date = comment.created_at
        if date not in results.keys():
            results[date] = {'total_comments': 0, 'blocked_comments': 0}
        results[date]['total_comments'] += 1

        if comment.blocked:
            results[date]['blocked_comments'] += 1

    result_list = [{'date': date, **data} for date, data in results.items()]
    return result_list


async def update_comment(
    comment_id: int,
    body: CommentBase,
    user: User,
    db: Session
) -> Comment:
    """
    The update_comment function updates a comment.

    :param comment_id: The comment id
    :param body: The comment data
    :param user: The current user
    :param db: The database session
    :return: The updated comment
    """
    comment = db.query(Comment).filter(and_(
        Comment.id == comment_id, Comment.user_id == user.id
    )).first()
    comment.text = body.text
    db.commit()
    return {'comment': comment, 'detail': 'Comment updated successfully'}


async def delete_comment(
    comment_id: int,
    user: User,
    db: Session
) -> dict:
    """
    The delete_comment function deletes a comment.

    :param comment_id: The comment id
    :param user: The current user
    :param db: The database session
    :return: The deleted comment
    """
    comment = db.query(Comment).filter(and_(
        Comment.id == comment_id, Comment.user_id == user.id
    )).first()
    db.delete(comment)
    db.commit()
    return {'comment': comment, 'detail': 'Comment deleted successfully'}
