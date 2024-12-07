from pydantic import BaseModel

class ServiceResponseModel(BaseModel):
    inton_percentage: float = 0.0
    pause: float = 0.0
    temp1: float = 0.0
    friendliness: float = 0.0
    emph: float = 0.0
    texts: list[str] | None = None
    gtext1: float = 0.0
    audio_path: str | None
    err_text: str | None = None
    
    class Config:
        extra = "ignore"  # Automatically ignore extra fields