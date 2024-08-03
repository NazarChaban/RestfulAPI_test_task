"""
This module contains the API routes related to user authentication.

It includes the following routes:
- `/auth/signup`: Creates a new user in the database.
- `/auth/login`: Authenticates a user and returns an access token.
- `/auth/refresh-token`: Refreshes the access token.
- `/auth/confirm-email/{token}`: Confirms a user's email address.
- `/auth/request-email`: Sends an email to the user with a link to confirm their account.
"""
from fastapi import (
    APIRouter, HTTPException, Depends, status,
    Security, BackgroundTasks, Request
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
import src.repository.users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email
from src.database.db import get_db

router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post(
    '/signup', response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    The signup function creates a new user in the database.

    :param body: Get the data from the request body
    :param background_tasks: Add a task to the background tasks queue
    :param request: Get the base url of the server
    :param db: Pass the database session to the repository
    :return: A dictionary
    """
    is_user_existing = await repository_users.get_user_by_email(body.email, db)
    if is_user_existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User already exists'
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return {
        'user': new_user,
        'detail': 'User created successfully. Check your email for confirmation'
    }


@router.post(
    '/login', response_model=TokenModel,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    The login function is used to authenticate a user.
    It takes in the email and password of the user, and returns an access
    token if successful.

    :param body: Get the email and password from the request body
    :param db: Access the database
    :return: A dictionary with the following keys:
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email is not confirmed"
        )

    access_token = await auth_service.create_access_token(user.email)
    refresh_token = await auth_service.create_refresh_token(user.email)
    await repository_users.update_token(user, refresh_token, db)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }


@router.get(
    '/refresh-token', response_model=TokenModel,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """
    The refresh_token function is used to refresh the access token.
    It takes in a refresh token and returns an access_token, a new
    refresh_token, and the type of token (bearer).

    :param credentials: Get the token from the request header
    :param db: Get the database session
    :return: A dictionary with the access_token, refresh_token and token_type
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    access_token = await auth_service.create_access_token(user.email)
    refresh_token = await auth_service.create_refresh_token(user.email)
    await repository_users.update_token(user, refresh_token, db)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }


@router.get(
    '/confirm-email/{token}',
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def confirm_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    The confirm_email function is used to confirm a user's email address.

    :param token: Get the token from the url
    :param db: Get the database connection
    :return: A dictionary with message 'Your email is already confirmed' or 'Email confirmed'
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification error"
        )
    if user.confirmed:
        return {'message': 'Your email is already confirmed'}
    await repository_users.confirm_email(email, db)
    return {'message': 'Email confirmed'}


@router.post(
    '/request-email',
    dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    The request_email function is used to send an email to the user with a link
    to confirm their account.

    The function takes in the body of the request,
    which contains only one field: email. It then uses this information to
    query for a user in our database and if it finds one, sends them an email
    with a link that they can use to confirm their account.

    :param body: Validate the request body
    :param background_tasks: Add a task to the background queue
    :param request: Get the base_url of the application
    :param db: Create a database session
    :return: A dictionary with a message 'Check your email for confirmation' or 'Your email already confirmed'
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {'message': 'Your email already confirmed'}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {'message': 'Check your email for confirmation'}
