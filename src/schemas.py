"""
This module contains the schema definitions for the RESTful API.

The schemas define the structure and validation rules for the data models used in the API.
These models include Post, Comment, User, Token, Email, and AI items.

Each schema is defined as a Pydantic BaseModel subclass, which provides a way
to define the fields, their types, and any validation rules.

The module includes the following schemas:

- PostBase: Base schema for a post, with a text field.
- PostDB: Database schema for a post, with additional fields for id, created_at, and user_id.
- PostResponse: Response schema for a post, including the post and a detail message.

- CommentBase: Base schema for a comment, with a text field.
- CommentCreate: Schema for creating a comment, with additional fields for response_on_comment and post_id.
- CommentDB: Database schema for a comment, with additional fields for id, created_at, blocked, block_reason, response_on_comment, post_id, and user_id.
- CommentResponse: Response schema for a comment, including the comment and a detail message.

- UserModel: Schema for a user, with fields for username, email, and password.
- UserDB: Database schema for a user, with additional fields for id, username, email, and avatar.
- UserResponse: Response schema for a user, including the user and a detail message.

- TokenModel: Schema for a token, with fields for access_token, refresh_token, and token_type.

- RequestEmail: Schema for requesting an email, with a field for the email address.

- PostAiModel: Schema for an AI-generated post, with a post_text field.
- CommentAiModel: Schema for an AI-generated comment, with fields for post_text and comment_text.

These schemas are used to define the structure of the data sent and received by the API endpoints.
"""
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


# Post schemas
class PostBase(BaseModel):
    text: str = Field(max_length=1024)


class PostDB(PostBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    post: PostDB
    detail: str


# Comment schemas
class CommentBase(BaseModel):
    text: str = Field(max_length=255)


class CommentCreate(CommentBase):
    response_on_comment: Optional[int]
    post_id: int


class CommentDB(CommentBase):
    id: int
    created_at: datetime
    blocked: bool
    block_reason: Optional[str]
    response_on_comment: Optional[int]
    post_id: int
    user_id: int

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    comment: CommentDB
    detail: str


class CommentDailyBreakdown(BaseModel):
    date: datetime
    total_comments: int
    blocked_comments: int


# User schemas
class UserModel(BaseModel):
    username: str = Field(max_length=255)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=255)


class UserDB(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDB
    detail: str


# Token schemas
class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


# Email schemas
class RequestEmail(BaseModel):
    email: EmailStr


# AI items schemas
class PostAiModel(BaseModel):
    post_text: str


class CommentAiModel(PostAiModel):
    post_text: str
    comment_text: str
