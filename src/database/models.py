"""
This module contains the models for the database tables
"""
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship, declarative_base
)
from sqlalchemy import String, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime

Base = declarative_base()


class Post(Base):
    """
    The Post class is used to creatre a post table in the database
    """
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(1024))
    created_at: Mapped[DateTime] = mapped_column(DateTime)
    blocked: Mapped[bool] = mapped_column(default=False)
    block_reason: Mapped[str | None]
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    user: Mapped['User'] = relationship('User', backref='posts')


class Comment(Base):
    """
    The Comment class is used to create a comment table in the database
    """
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DateTime)
    blocked: Mapped[bool] = mapped_column(default=False)
    block_reason: Mapped[str | None]
    response_on_comment: Mapped[int | None] = mapped_column(
        ForeignKey('comments.id', ondelete='CASCADE'), default=None
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey('posts.id', ondelete='CASCADE')
    )
    post: Mapped['Post'] = relationship('Post', backref='comments')
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    user: Mapped['User'] = relationship('User', backref='comments')


class User(Base):
    """
    The User class is used to create a user table in the database
    """
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(default=False)
    auto_response: Mapped[bool] = mapped_column(default=False)
    response_interval: Mapped[int] = mapped_column(default=300)
    refresh_token: Mapped[str | None]
    confirmed: Mapped[bool] = mapped_column(default=False)
