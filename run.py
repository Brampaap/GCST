import json, time
from test.test_service_mock import service

import streamlit as st
import streamlit.components.v1 as components
from langchain.chat_models.gigachat import GigaChat
from core.chat import TaskLoader

import core.lib.streamlit.components as st_inner
from core import critique, front
from core.lib.streamlit import utils
from core.chat import Chat, Message, Task
from core.lib import constants, datacls, exercise
from core.lib.exercise.default import dialog
from core.lib.pipeline import Pipeline
from core.service import Service, ServiceResponseModel

# Общие настройки страницы
st.set_page_config(
    page_title="RapportTop",
    page_icon="👨‍💼"
)

# main.css
st.markdown(
    front.main_css,
    unsafe_allow_html=True,
)

try:  # Скрываем все видимые ошибки UI
    # Инициализация кастомной компоненты (кнопка записи / продолжения)
    record_button = components.declare_component("custom_input", path="build")
    context = st.session_state
    secrets = st.secrets

    # Инициализация чата
    if context.get("chat") is None:
        context.chat = Chat(context=context)
        context.service = Service(context=context, secrets=secrets)

        # << ----- Чтение входных данных ----- >>
        # Комментарий, который выводится под title, указан по требованию бизнеса
        context.comment = st.query_params.get("comment")
        context.course_id = st.query_params.get("course_id", 3)

        # Получение диалогов
        if context.course_id:
            context.tasks = TaskLoader(context=context, secrets=secrets).load()
        else: # Дефолтный сеттинг задач
            context.tasks = [Task(**item) for item in dialog]
        assert len(context.tasks), "No tasks provided!"

        context.progress_text = "" # Дефолтный контент прогресс бара
        context.current_task_index = -1  # Индекс исполняемого диалога
        context.task_scores = []  # Счёт баллов за задания
        context.synchronize = False
        context.streamlit_crutch = False

        # << ----- Инициализация моделей ----- >>
        model_config = dict(
            credentials=st.secrets["GIGAAUTH"],
            verify_ssl_certs=False,
            scope="GIGACHAT_API_CORP",
            temperature=1e-8,
            model="GigaChat-Max",
        )

        # Основная модель
        context.pro_model = GigaChat(**model_config)
        # Lite модель
        del model_config["model"]
        context.lite_model = GigaChat(**model_config)

        context.pipeline = Pipeline()

        # Инициализация всех степов пайплайна проверки
        context.pipeline.steps.extend(
            [
                critique.EloquenceProcessor(
                    model=context.pro_model,
                ),
                critique.SemanticSimProcessor(
                    model=context.pro_model,
                    emb_secret=secrets["GIGAAUTH"],
                ),
                critique.ССSProcessor(model=context.pro_model),
                critique.IntonProcessor(context=context),
                critique.TempProcessor(context=context),
                critique.FriendlinessProcessor(context=context),
            ]
        )
        
        context.typo_processor = critique.TypoProcessor(model=context.lite_model)

        # << ----- Отправка сигнала "ready" в LMS ----- >>
        status = datacls.Status(status="ready")
        st_inner.run_js_script(status.model_dump_json())

    if context.comment:
        st.markdown(context.comment)
    st.header("Тренажёр голосового чата")
    
    chat = context.chat
    pipeline = context.pipeline

    top_container = st.empty()
    # Not comment используется для адаптации на телефоне
    if chat.n_messages == 0 and not context.comment:
        top_container.image("core/front/img/chat_bg.svg", use_container_width=True)
    elif chat.n_messages == 0 and context.comment:
        top_container.empty()
    elif context.current_task_index + 1 <= len(context.tasks):
        progress_text = f"Прогресс: {context.current_task_index + 1}/{len(context.tasks)}"
        top_container.progress((context.current_task_index + 1) / len(context.tasks), text=progress_text)

    delay_to_record = chat.show()

    # Основной цикл приложения
    if context.current_task_index < chat.n_tasks:
        if context.get("recorded_audio") is not None:
            record = context.recorded_audio

            # Вывод результата ASR ответа ученика
            role = "user"
            avatar = "👨‍🏫"
            with st.chat_message(name=role, avatar=avatar):
                with st.spinner(text="Распознавание..."):
                    result: int | ServiceResponseModel | str = context.service.run(record, context.current_task.right_answer)

                    if isinstance(result, str):
                        st.write("Ошибка распознавания. Убедитесь в хорошем качестве записи с вашего микрофона.")
                        st.audio(f"{secrets['ZAIKANIE_URL']}/{result}", autoplay=True)
                        
                        # Показать аудио пользователю
                        st.markdown(
                            front.show_audio_css,
                            unsafe_allow_html=True,
                        )
                        st.button(
                            "↻ Повтор",
                            on_click=lambda: utils.reset_empty_input(context),
                            key="empty_reset",
                            use_container_width=True,
                        )
                        raise(LookupError("Bad recognition")) # Остановить выполнение без ошибок
                    elif result == 500:
                        raise(RuntimeError("500 Remote Service Response"))
                    else:
                        _, result.texts[0] = context.typo_processor.run_model(result.texts[0])
                        st.write(result.texts[0])
                        context.service_result = result

                        message = Message(
                            role=role,
                            avatar=avatar,
                            content_type=["text"],
                            content=[result.texts[0]],
                        )

                        chat.add_message(message=message)

            # Вывод результата анализа
            role = "assistant"
            avatar = "🤖"
            with st.chat_message(name=role, avatar=avatar):
                with st.spinner(text="Анализирую ваш ответ..."):
                    scores, responses, step_success = pipeline.run(context=context)
                task_score = min(
                    round(sum(scores) / sum(step_success)),
                    constants.MAX_TASK_SCORE,
                )
                score_string = exercise.score_message.format(
                    task_score=task_score, max_score=constants.MAX_TASK_SCORE
                )
                text = constants.LF.join(
                    [constants.CHAT_PREFIX, *responses, score_string]
                )

                right_answer_expander = {
                    "label": "Верный ответ",
                    "text": context.current_task.right_answer,
                }

                message = Message(
                    role=role,
                    avatar=avatar,
                    content_type=["text", "expand"],
                    content=[text, right_answer_expander],
                )

                chat.add_message(message=message)
                context.task_scores.append(task_score)

                # Очищаю значение как признак того, что оно обработано
                context.recorded_audio = None
                st.rerun()

        if not context.get("continueMode", True):
            # Задержка до появления кнопки записи нужно для того, чтобы ученик дослушал запись
            if not context.streamlit_crutch: # Костыль для того, чтобы 
                time.sleep(delay_to_record)
            else:
                context.streamlit_crutch = False

            record_button(
                key="recorded_audio", continueMode=False, state=context.synchronize
            )

            context.continueMode = True
            if context.synchronize:
                context.continueMode = False
                context.synchronize = False
                context.streamlit_crutch = True
                st.rerun()
        else:
            # Переход к следующему заданию
            context.current_task_index += 1

            if context.current_task_index == chat.n_tasks:
                st.rerun()  # Скрыть кнопку

            context.current_task = context.tasks[context.current_task_index]

            message = Message(
                role="assistant",
                avatar="👨‍💼",
                content_type=["text", "audio"],
                content=[context.current_task.message, context.current_task.audio],
            )
            chat.add_message(message)
            record_button(key="continueMode", continueMode=True)
        # Скролл вниз
        st_inner.run_js_script(front.scroll)

    else:
        # Вывод итогового результата и отправка его LMS
        role = "assistant"
        avatar = "🤖"
        with st.chat_message(name=role, avatar=avatar):
            percent_result = round(sum(context.task_scores) / chat.n_tasks, 2)

            st.write("Задание завершено, спасибо!")
            st.markdown(
                f"""<h1 align="center">Ваш балл: {percent_result}%</h1>""",
                unsafe_allow_html=True,
            )

            # Отправка данных на сервер
            response = datacls.ResultData(
                score=sum(context.task_scores),
                max_score=len(context.task_scores) * constants.MAX_TASK_SCORE,
            )

            compiled_result_script = front.post_message_template.format(
                response_json=response.model_dump_json()
            )
            st_inner.run_js_script(compiled_result_script)
        # Скролл вниз
        st_inner.run_js_script(front.scroll)
except LookupError:
    st.stop()
# except Exception as e:
#     print(e)
#     st.error("Internal server error")
#     st.stop()
