from pydantic import BaseModel

class ServiceResponseModel(BaseModel):
    inton_precentage: float | None = None
    pause: float | None = None
    temp: float | None = None
    dusha: list[float] | None = None
    emph: float | None = None
    texts: list[str] | None = None
    gtext1: float | None = None
    audio_path: str | None
    err_text: str | None = None
    
    class Config:
        extra = "ignore"  # Automatically ignore extra fields