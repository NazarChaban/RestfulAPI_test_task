"""
This module contains the Auth class, which is used for authentication-related
operations such as hashing passwords, creating and verifying tokens, and
retrieving user information.

The Auth class provides the following methods:
- verify_password(plain_password, hashed_password): Verifies if a plain-text password matches a hashed password.
- get_password_hash(password): Returns the hash of a given password.
- create_token(username, delta, scope): Creates a JWT token with the specified payload.
- create_access_token(username): Creates a new access token for a user.
- create_refresh_token(username): Creates a refresh token for a user.
- create_email_token(email): Creates a token for a given email address.
- decode_refresh_token(refresh_token): Decodes a refresh token and returns the associated email address.
- get_current_user(token, db): Retrieves the current user based on the provided token and database session.
- get_email_from_token(token): Retrieves the email address associated with a given token.
"""
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.repository import users as repository_users
from src.conf.config import settings
from src.database.db import get_db


class Auth:
    """
    The Auth class is used to hash passwords, create tokens, and verify tokens.
    """
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/post-manager/auth/login')

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ):
        """
        The verify_password function takes a plain-text password and a hashed
        password, and returns True if the plain-text password matches the
        hashed

        :param self: Represent the instance of the class
        :param plain_password: Pass in the plain text password that the user has entered
        :param hashed_password: Pass in the hashed password from the database
        :return: True if the password is correct and False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns
        the hash of that password.

        :param self: Represent the instance of the class
        :param password: Get the password from the user
        :return: A hash of the password
        """
        return self.pwd_context.hash(password)

    async def create_token(
        self,
        username: str,
        delta: timedelta,
        scope: str
    ):
        """
        The create_token function creates a JWT token with the payload

        :param self: Represent the instance of the class
        :param username: Create a payload with the username
        :param delta: Set the time when the token will expire
        :param scope: Determine the scope of the token
        :return: A jwt token
        """
        cur_time = datetime.now(timezone.utc)
        expiration_time = cur_time + delta

        payload = {
            'sub': username,
            'iat': cur_time,
            'exp': expiration_time,
            'scope': scope
        }

        jwt_token = jwt.encode(
            payload, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return jwt_token

    async def create_access_token(self, username: str):
        """
        The create_access_token function creates a new access token for the
        user.

        :param self: Represent the instance of the class
        :param username: Identify the user
        :return: A token, which is a string
        """
        return await self.create_token(
            username, timedelta(minutes=15), 'access_token'
        )

    async def create_refresh_token(self, username: str):
        """
        The create_refresh_token function creates a refresh token for the user.

        :param self: Represent the instance of the class
        :param username: Create a refresh token for the user
        :return: A refresh token that expires in 7 days
        """
        return await self.create_token(
            username, timedelta(days=7), 'refresh_token'
        )

    async def create_email_token(self, email: str):
        """
        The create_email_token function creates a token for the given email.
        The token is valid for 7 days and has the 'email_scope' scope.

        :param self: Represent the instance of the class
        :param email: Specify the email address of the user
        :return: A token
        """
        return await self.create_token(
            email, timedelta(days=7), 'email_scope'
        )

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function is used to decode the refresh token.

        :param self: Represent the instance of the class
        :param refresh_token: Pass the refresh token to the function
        :return: The email of the user who is requesting a new access token
        """
        try:
            payload = jwt.decode(
                refresh_token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM]
            )
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid scope for token'
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Could not validate credentials'
            )

    async def get_current_user(
            self,
            token: str = Depends(oauth2_scheme),
            db: Session = Depends(get_db)
    ):
        """
        The get_current_user function is a dependency that will be used in the

        :param self: Represent the instance of a class
        :param token: Get the token from the authorization header
        :param db: Pass the database session to the function
        :raise credentials_exception: If the credentials are invalid
        :return: The user object
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM]
            )
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and
        returns the email address associated with that token.
        The function first decodes the JWT using our SECRET_KEY and ALGORITHM,
        then checks to make sure that the scope is correct.
        If it is not, we raise an HTTPException with status code 401
        (Unauthorized) and detail message 'Invalid scope for token'.
        If everything goes well, we return payload['sub'], which contains the
        email address.

        :param self: Represent the instance of the class
        :param token: Pass the token to the function
        :return: The email address from the token
        """
        try:
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM]
            )
            if payload['scope'] != 'email_scope':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Invalid scope for token'
                )
            return payload['sub']
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Invalid token for email verification'
            )

auth_service = Auth()
