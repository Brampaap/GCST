import requests
import base64
from core.service.datacls import ServiceResponseModel
import io
from pydub import AudioSegment

class Service():
    def __init__(self, context, secrets):
        self.context = context
        self.secrets = secrets

    def make_query(self, audio: str, right_answer: str) -> None | ServiceResponseModel:
        
        encoded = base64.b64decode(audio.split(",")[1])
        a_segment = AudioSegment.from_file(io.BytesIO(encoded))
        
        # Преобразуем к целевым параметрам
        a_segment = (a_segment.set_frame_rate(16000)
                    .set_channels(1)
                    .set_sample_width(2))
        
        # Сохраняем результат в буфер памяти
        output_buffer = io.BytesIO()
        a_segment.export(output_buffer, format="wav")
        output_buffer.seek(0)

        data = {
            "key": self.secrets["SERVICE_KEY"],
            "text1": right_answer,
            "lang": "ru",
        }

        response = requests.post(
            f"{self.secrets['ZAIKANIE_URL']}/audio.php", 
            data=data, 
            files={
                "file": output_buffer.read(),
            },
        )

        if not response.ok or response.json().get("err_code") == "1":
            return None
        response = response.json()
        response = ServiceResponseModel(**response, extra="ignore")

        return response

    def run(self, audio: bytes, right_answer: str) -> int | ServiceResponseModel | str:
        response = self.make_query(audio, right_answer)

        if response is None:
            return 500
        elif response.err_text is None:
            return response
        else:
            return response.audio_path
