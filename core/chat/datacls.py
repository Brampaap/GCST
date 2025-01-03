import base64
from typing import Literal

from pydantic import BaseModel, model_validator, Field


class Message(BaseModel):
    role: Literal["user", "assistant"]
    avatar: Literal["🤖", "👨‍🏫", "👨‍💼"]
    content_type: list[str]
    content: list[str | dict]

    @model_validator(mode="after")
    def validate_content(self):
        white_list = ("text", "expand", "audio", "recognition_error")
        if self.content_type == "text" and not isinstance(self.content, str):
            raise ValueError("Content must be a string when content_type is 'text'")
        elif self.content_type == "expand" and not isinstance(self.content, dict):
            raise ValueError(
                "Content must be a dictionary when content_type is 'expand'"
            )
        elif not all(
            [item in white_list for item in self.content_type]
        ):
            raise ValueError(
                f'content_type must be one of available values {white_list}'
            )
        return self

class AnswerText(BaseModel):
    answer_text: str
    weight: int

class SpeechParams(BaseModel):
    inton_min: int | None = None
    inton_max: int | None = None
    temp_min: int | None = None
    temp_max: int | None = None
    show_friendliness: int | None = None

class Task(BaseModel):
    message: str
    audio: str
    speech_params: SpeechParams = Field(default_factory=SpeechParams)
    answers: list[AnswerText] = Field(alias="answers")

    @property
    def right_answer(self) -> str:
        # Возвращает текст первого ответа
        if self.answers:
            return self.answers[0].answer_text
        raise ValueError("Список answers пуст.")