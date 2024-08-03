"""
This module contains services related to AI moderation and comment response.

It provides the following classes and functions:
- moderate_content: A function that moderates the content of a comment or post.
- comment_response: A function that generates a response to a comment.
- CommentPool: A class that represents a pool of comments to be processed.

The module also defines dictionaries for moderate content handlers and response handlers,
which map AI names to their corresponding moderation and response functions.
"""
from datetime import datetime
from typing import Callable
import asyncio
from sqlalchemy.orm import Session
from fastapi import Depends

from src.services.ai import claude_ai, gemini_ai, gpt_or_llama_ai
from src.schemas import CommentAiModel, PostAiModel
from src.database.models import Post, Comment
from src.conf.config import settings
from src.database.db import get_db

moderate_content_handlers = {
    'claude': claude_ai.moderate_content,
    'gemini': gemini_ai.moderate_content,
    'gpt': gpt_or_llama_ai.moderate_content,
    'llama': gpt_or_llama_ai.moderate_content
}

response_handlers = {
    'claude': claude_ai.comment_response,
    'gemini': gemini_ai.comment_response,
    'gpt': gpt_or_llama_ai.comment_response,
    'llama': gpt_or_llama_ai.comment_response
}


class CommentPool:
    """
    The CommentPool class is a pool of comments that need to be processed.
    """
    def __init__(self):
        self.queue = asyncio.Queue()
        self.task = None
        self.is_running = False

    async def add_comment(
        self,
        comment,
        post,
        interval: int,
        response_func: Callable
    ):
        """
        The add_comment function adds a comment to the pool.
        """
        await self.queue.put((comment, post, interval, response_func))

    async def process_comments(self):
        """
        The process_comments function processes the comments in the pool.
        """
        while self.is_running:
            try:
                comment, post, interval, response_func = await asyncio.wait_for(
                    self.queue.get(), timeout=1.0
                )
                await asyncio.sleep(interval)
                await response_func(comment, post)
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue

    async def start(self):
        """
        The start function starts the comment pool.
        """
        if not self.is_running:
            self.is_running = True
            self.task = asyncio.create_task(self.process_comments())

    async def stop(self):
        """
        The stop function stops the comment pool.
        """
        if self.is_running:
            self.is_running = False
            if self.task:
                await self.task
                self.task.cancel()


comment_pool = CommentPool()


async def moderate_content(
    item: CommentAiModel | PostAiModel,
) -> dict:
    """
    The moderate_content function moderates the content of a comment.

    :param text: The text of the comment
    :param user: The current
    :param db: The database session
    :return: The moderation result
    """
    handler = moderate_content_handlers[settings.ai_used]
    result = await handler(item)
    return result


async def comment_response(
    comment: Comment,
    post: Post,
    db: Session = Depends(get_db)
):
    """
    The comment_response function generates a response to a comment.

    :param item: The comment
    :return: The response
    """
    handler = response_handlers[settings.ai_used]
    comment_for_ai = CommentAiModel(
        post_text=post.text,
        comment_text=comment.text
    )
    response = await handler(comment_for_ai)

    new_comment = Comment(
        text=response,
        created_at = datetime.now().strftime('%d-%m-%Y'),
        response_on_comment=comment.id,
        user_id=post.user_id,
        post_id=post.id
    )
    db.add(new_comment)
    db.commit()
