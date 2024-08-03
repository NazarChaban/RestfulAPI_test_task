"""
This module contains functions for content moderation and generating responses using the Gemini AI model.

The module includes the following functions:
- check_content: Analyzes the given item for inappropriate content.
- moderate_content: Moderates the content of a post or comment item with Gemini AI.
- comment_response: Generates a response for the given comment with Gemini AI.
"""
from fastapi import HTTPException, status
import google.generativeai as genai
from typing import Union
import json

from src.schemas import PostAiModel, CommentAiModel
from src.conf.config import settings

genai.configure(api_key=settings.ai_api_key)
model = genai.GenerativeModel(settings.ai_model)


async def check_content(item) -> dict:
    """
    Analyzes the given item for inappropriate content.
    The return dictionary has the following keys:
    - "is_acceptable": A boolean value indicating whether the content is acceptable or not.
    - "explanation": A short explanation justifying the decision.

    :param item: The item to be analyzed. It can be either a PostAiModel or a CommentAiModel.
    :return: A dictionary containing the analysis result.
    :raises: HTTPException If there is an error in content moderation.

    """
    try:
        if isinstance(item, PostAiModel):
            prompt = f"""
            Проаналізуй наступний текст посту на веб форумі на наявність:

            1. Нецензурної лексики
            2. Образ або дискримінації
            3. Загроз або закликів до насильства
            4. Спаму або неприйнятної реклами

            Поверни True, якщо текст прийнятний, або False, якщо він містить неприйнятний вміст а також коротке пояснення свого рішення.
            Відповідь має бути у форматі:
            {"is_acceptable": True/False, "explanation": "Коротке обґрунтування рішення"}

            Текст: {item.post_text}
            """
        elif isinstance(item, CommentAiModel):
            prompt = f"""
            Проаналізуй наступний коментар:

            "{item.comment_text}"

            До цього поста на веб форумі:

            "{item.post_text}"

            Визнач, чи містить цей коментар будь-що з наступного:
            1. Нецензурну лексику
            2. Образи або дискримінацію
            3. Загрози або заклики до насильства
            4. Спам або неприйнятну рекламу

            Поверни відповідь у форматі:
            {"is_acceptable": True/False, "explanation": "Коротке обґрунтування рішення"}
            """

        response = model.generate_content(
            contents=[
                {
                    'role': 'system',
                    'parts': ['You are a content moderation assistant.']
                },
                {'role': 'user', 'parts': [prompt]}
            ]
        )
        return json.loads(response.text)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in content moderation: {str(err)}"
        )


async def moderate_content(item: Union[PostAiModel, CommentAiModel]) -> dict:
    """
    Moderates the content of a post or comment item with gemini ai.

    :param item: The post or comment item to be moderated.
    :return dict: The result of the content moderation.
    :reises: HTTPException If there is an HTTP exception or unexpected error during the moderation process.
    """
    try:
        result = await check_content(item)
        return result
    except HTTPException as herr:
        raise herr
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(err)}"
        )


async def comment_response(item: CommentAiModel) -> dict:
    """
    Generates a response for the given comment with gemini ai.

    :param item: The comment item to generate a response for.
    :return: A dictionary containing the generated response.
    :raises: HTTPException if there is an error in generating the response.
    """
    prompt = f"""
    Проаналізуй наступний коментар:

    "{item.comment_text}"

    До цього поста на веб форумі:

    "{item.post_text}"

    Дай прийнятну відповідь на цей коментар. Віповідь обов'язково має бути в контексті коментаря та поста.
    """

    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in generating response: {str(err)}"
        )
