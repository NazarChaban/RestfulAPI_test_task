"""
This module contains the main FastAPI application for the RestAPI post manager app.

It includes the necessary routes and services to handle authentication,
user management, post management, and comment management.

The module also defines a lifespan function that initializes and closes
resources, such as a Redis connection and a comment pool. The lifespan
function is used by the FastAPI application to manage the lifecycle of these resources.

The module also defines a root route handler that returns a welcome message
when the application is accessed.

To run the application, execute this module directly.

Example:
    python main.py
"""
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
import redis.asyncio as aioredis
from fastapi import FastAPI
import uvicorn

from src.routes import comments, auth, users, posts
from src.services.ai_services import comment_pool
from src.conf.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    The lifespan function is a coroutine that runs before and after the
    application.
    It's used to initialize and close resources, such as redis connection, etc.

    :param app: Pass the fastapi instance to the function
    :return: An object that can be used to clean up the resources when the server shuts down
    """
    r = await aioredis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0
    )
    await FastAPILimiter.init(r)
    await comment_pool.start()
    yield
    await comment_pool.stop()
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix='/post-manager')
app.include_router(users.router, prefix='/post-manager')
app.include_router(posts.router, prefix="/post-manager")
app.include_router(comments.router, prefix="/post-manager")


@app.get('/')
async def read_root():
    """
    The read_root function returns a dictionary with the key 'message' and
    value 'Welcome to RestAPI post manager app'.

    :return: A dictionary
    """
    return {'message': 'Welcome to RestAPI post manager app'}


if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
