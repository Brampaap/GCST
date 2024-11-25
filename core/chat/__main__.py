import streamlit as st
from streamlit.runtime.secrets import Secrets

# https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
from streamlit.runtime.state.session_state_proxy import SessionStateProxy

from core.chat.datacls import Message
from core.lib import constants
from core.lib.streamlit import utils


class Chat:
    def __init__(self, context: SessionStateProxy, secrets: Secrets) -> None:
        self.context = context
        self.messages: list[Message] = []

    def add_message(self, message: Message):
        self.messages.append(message)

    def reset_last_message(self):
        if not self.context.synchronize:
            self.context.synchronize = True
            self.context.current_task_index -= 1
            self.context.current_task = self.context.tasks[self.context.current_task_index]
            self.messages = self.messages[
                : self.context.current_task_index * constants.MESSAGES_PER_TASK + 1
            ]
            self.context.continueMode = False
            self.context.task_scores.pop()

    def validate_context(self): ...

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
        else:
            duration_seconds = 0
            if self.messages and self.messages[-1].content_type[-1] == "audio":
                waveform, sample_rate, duration_seconds = utils.load_base64_audio(
                    message.content[-1]
                )
                st.audio(waveform, sample_rate=sample_rate, autoplay=True)
        return duration_seconds

    @property
    def n_tasks(self) -> int:
        return len(self.context.tasks)

    @property
    def n_messages(self) -> int:
        return len(self.messages)
