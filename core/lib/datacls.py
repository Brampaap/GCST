from typing import Any

from pydantic import BaseModel, model_serializer


class ResultData(BaseModel):
    """Формат результата ответа"""

    score: int
    max_score: int

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {"result": [self.score, self.max_score]}


class Status(BaseModel):
    """Статус, отправляемый на сервер"""

    status: str
