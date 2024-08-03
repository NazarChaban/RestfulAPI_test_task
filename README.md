# Post-manager API

## Description

This project is a RESTful API that provides the ability to manage posts and comments.
Also there are AI moderation of posts and comments and AI auto responses on comments.


## Installation

To use this API, follow these steps:

1. Clone the repository: `git clone https://github.com/Vivern0/RestfulAPI_test_task.git`
2. Initialise poetry environment: `poetry shell`
3. Install the required dependencies: `poetry install --no-root`
4. Set up your credentials: see .env_exmp
5. Run database and redis: `docker compose up`
6. Set up the database: `alembic upgrade head`
7. Start the app: `python main.py`

## Usage

To use the API, follow these steps:

1. Make sure the server is running.
2. Send HTTP requests to the appropriate endpoints using your preferred tool (e.g., Postman, cURL, etc.).
3. Enjoy!

## Endpoints example

### Authentication

- **Signup**
    ```http
    POST /post-manager/auth/signup
    ```
    **Request Body**:
    - `username`: String
    - `email`: String
    - `password`: String

- **Login**
    ```http
    POST /post-manager/auth/login
    ```
    **Request Body**:
    - `username`: String (email in this case)
    - `password`: String

- **Refresh Token**
    ```http
    GET /post-manager/auth/refresh_token
    ```
    **Headers**:
    - `Authorization`: Bearer <refresh_token>

### Users

- **Get Your Profile Info**
    ```http
    GET /post-manager/users/me
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Update Auto Response**
    ```http
    POST /post-manager/users/auto-response?response=True|False&response_interval={seconds}
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Delete Account**
    ```http
    DELETE /post-manager/users/me/delete
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

### Posts

- **Create Post**
    ```http
    POST /post-manager/posts/
    ```
    **Request Body**:
    - `text`: String
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Get Posts**
    ```http
    GET /post-manager/posts/?limit={>=0}&offset={>=0}&descending=True|False
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Search By Text Or Author**
    ```http
    GET /post-manager/posts/search
    ```
    **Request Body**
    - `text`: String
    - `author`: String
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Get Post By Id**
    ```http
    GET /post-manager/posts/{post_id}
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Get Post By Username**
    ```http
    GET /post-manager/posts/user/{user_name}
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Update Post**
    ```http
    PATCH /post-manager/posts/{post_id}
    ```
    **Request Body**:
    - `text`: String
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Delete Post**
    ```http
    DELETE /post-manager/posts/{post_id}
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

### Comments

- **Add Comment**
    ```http
    POST /post-manager/comments/
    ```
    **Request Body**:
    - `text`: String
    - `response_on_comment`: Integer (0 if it is not a response on someones comment)
    - `post_id`: Integer

    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Get Your Comments**
    ```http
    GET /post-manager/comments/
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Get Comment By Id**
    ```http
    GET /post-manager/comments/{comment_id}
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Get Comments By User Id (only for admin or comment's author)**
    ```http
    GET /post-manager/comments/for-user/{user_id}
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Get Comments By Post Id**
    ```http
    GET /post-manager/comments/for-post/{post_id}
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Get Daily Breakdown**
    ```http
    GET /post-manager/comments/daily-breakdown/{post_id}?date_from={yyyy.mm.dd}&date_to={yyyy.mm.dd}
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Edit Comment**
    ```http
    PATCH /post-manager/comments/{comment_id}
    ```
    **Request Body**:
    - `text`: String

    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Delete Comment**
    ```http
    DELETE /post-manager/comments/{comment_id}
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

## Documentation

For detailed documentation on the API endpoints and their functionalities, you can open `index.html` by this path: `docs/_build/html/index.html`.
