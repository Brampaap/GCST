import base64
from typing import Literal

from pydantic import BaseModel, model_validator


class Message(BaseModel):
    role: Literal["user", "assistant"]
    avatar: Literal["🤖", "👨‍🏫", "👨‍💼"]
    content_type: list[str]
    content: list[str | dict]

    @model_validator(mode="after")
    def validate_content(self):
        if self.content_type == "text" and not isinstance(self.content, str):
            raise ValueError("Content must be a string when content_type is 'text'")
        elif self.content_type == "expand" and not isinstance(self.content, dict):
            raise ValueError(
                "Content must be a dictionary when content_type is 'expand'"
            )
        elif not all(
            [item in ("text", "expand", "audio") for item in self.content_type]
        ):
            raise ValueError(
                'content_type must be one of available values ("text", "expand", "audio)'
            )
        return self


class Task(BaseModel):
    message: str
    right_answer: str
    audio: str
    speech_params: dict

    @model_validator(mode="after")
    def validate_content(self):
        if not self.is_valid_mpeg(self.audio):
            raise ValueError("Audio must be an audio encoded into base64 format")
        return self

    def is_valid_mpeg(self, encoded_str):
        try:
            decoded_bytes = base64.b64decode(encoded_str.split(",")[1], validate=True)
            return True
        except (base64.binascii.Error, ValueError):
            return False
