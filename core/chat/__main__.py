import streamlit as st
from streamlit.runtime.secrets import Secrets
import requests
from io import BytesIO
import re
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
from streamlit.runtime.state.session_state_proxy import SessionStateProxy

from core.chat.datacls import Message, Task
from core.lib import constants
from core import front
from core.lib.streamlit import utils


class Chat:
    def __init__(self, context: SessionStateProxy) -> None:
        self.context = context
        self.messages: list[Message] = []

    def add_message(self, message: Message):
        self.messages.append(message)

    def reset_last_message(self):
        if not self.context.synchronize:
            self.context.synchronize = True
            self.context.streamlit_crutch = True
            self.context.current_task_index -= 1
            self.context.current_task = self.context.tasks[self.context.current_task_index]
            self.messages = self.messages[
                : self.context.current_task_index * constants.MESSAGES_PER_TASK + 1
            ]
            self.context.continueMode = False
            self.context.task_scores.pop()

    def reset_last_recognition(self):
        self.context.continueMode = False
        self.messages.pop()

    @staticmethod
    @st.cache_data(show_spinner="Загрузка аудио...")
    def download_audio_with_progress(url: str) -> BytesIO:
        """
        Добавлено предварительное скачивание для явного обозначения этого процесса.
        Пользователи с медленным интернетом ожидают в недоступном приложении до 20 секунд,
        нужна индикация.
        """
        chunk_size = 15 * 1024 * 1024

        response = requests.get(url, stream=True)
        response.raise_for_status()

        audio_data = BytesIO()

        downloaded = 0
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                audio_data.write(chunk)
                downloaded += len(chunk)

        audio_data.seek(0)

        return audio_data

    def show(self):
        for i, message in enumerate(self.messages, start=1):
            message: Message

            with st.chat_message(name=message.role, avatar=message.avatar):
                for content_type, content in zip(message.content_type, message.content):
                    if content_type == "text":
                        st.write(content)

                    elif content_type == "expand":
                        columns = st.columns([1])

                        if i == self.n_messages or i == (self.n_messages - 1):
                            columns = st.columns([1, 3])

                            with columns[0]:  # Кнопка reset
                                st.button(
                                    "↻ Повтор",
                                    on_click=self.reset_last_message,
                                    use_container_width=True,
                                )

                        with columns[-1]:
                            with st.expander(label=content["label"]):
                                st.markdown(
                                    utils.render_no_copy_text(text=content["text"]),
                                    unsafe_allow_html=True,
                                )
                    elif content_type == "recognition_error":
                        st.write("Ошибка распознавания. Убедитесь в хорошем качестве записи с вашего микрофона.")
                        st.audio(content, autoplay=True)

                        st.markdown(
                            front.show_audio_css,
                            unsafe_allow_html=True,
                        )
                        st.button(
                            "↻ Повтор",
                            on_click=lambda: self.reset_last_recognition(),
                            key="empty_reset",
                            use_container_width=True,
                        )
                        raise(LookupError("Bad recognition"))


        else:
            duration_seconds = 0
            if self.messages and self.messages[-1].content_type[-1] == "audio":
                task_text = self.messages[-1].content[-2]
                audio_data = Chat.download_audio_with_progress(message.content[-1])
                duration_seconds = self.estimate_speech_time(task_text)
                st.audio(audio_data, autoplay=True)
                
        return duration_seconds

    def estimate_speech_time(self, text: str, speech_rate: int = 150) -> float:
        """
        Оценка времени произношения текста.
        Необходимо ввиду того, что нужно сделать delay перед возможностью записи.
        """
        # Подсчёт слов
        words = re.findall(r'\b\w+\b', text)
        num_words = len(words)
        
        # Подсчёт предложений
        sentences = re.split(r'[.!?]', text)
        num_sentences = len([s for s in sentences if s.strip()])
        
        # Оценка времени
        words_per_second = speech_rate / 60
        base_time = num_words / words_per_second 
        pause_time = num_sentences * 0.5
        
        total_time = base_time + pause_time
        return round(total_time, 2)

    @property
    def n_tasks(self) -> int:
        return len(self.context.tasks)

    @property
    def n_messages(self) -> int:
        return len(self.messages)

class TaskLoader():
    def __init__(self, context: SessionStateProxy, secrets: Secrets) -> None:
        self.context = context
        self.url = f"{secrets['DS_URL']}/course"
        self.api_key = secrets["SERVICE_KEY"]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),  
        retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError))
    )
    def load(self):
        data = {
            "course_id": self.context.course_id,
            "key": self.api_key
        }
        response = requests.post(self.url, data=data)

        if not response.ok:
            response.raise_for_status()
        else: 
            response = response.json()["data"]["questions"]

        tasks = [Task(**item) for item in response]
            
        return tasks
