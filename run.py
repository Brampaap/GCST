import streamlit as st
import time
from streamlit.components.v1 import html
import streamlit.components.v1 as components
from modules.typos import processor as typo
from modules.semantic import proccesor as semantic_sim
from modules.common.prompt import global_prompt
from modules.common.parsers import score as score_parser
import constants

from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

import emoji

emoji_list = [
    "😊",
    "😊",
    "🙂",
    "😌",
    "😉",
    "😐",
    "😞",
    "🙁",
    "😔",
    "❄️",
    "⭐️",
    "🤗",
    "🌷",
    "🌺",
    "🌹",
    "☘️",
    "💐",
    "⏳️",
    "⌛️",
    "🚀",
    "☀️",
    "🌟",
    "🌞",
    "🔥",
    "⚡️",
    "✨️",
    "🎈",
    "🎉",
    "🎊",
    "🎁",
    "📍",
    "📌",
    "✅️",
    "☑️",
    "✔️",
    "💙",
    "🩵",
    "🤍",
    "👋",
    "🫶",
    "🙌",
    "💪",
    "🙏",
]

js_scroll = """
<script>
    itemsScrollTo = parent.window.document.getElementsByClassName("st-emotion-cache-0"); itemsScrollTo[itemsScrollTo.length-1].scrollIntoView();
</script>
"""

try:
    custom_input = components.declare_component("custom_input", path="./frontend")

    def reset_last_msg():
        st.session_state.input_msg = None
        st.session_state.show_input = True
        st.session_state.is_last_msg = False

        st.session_state.messages = st.session_state.messages[
            : st.session_state.answer_index
        ]
        st.session_state.answer_index -= 3

        st.session_state.dialog_index -= 1
        st.session_state.next_dialog = dialog[st.session_state.dialog_index]
        st.session_state.score.pop()
        st.session_state.show_reset_button = len(st.session_state.messages) > 1

    st.markdown(
        """
            <style>
            
            span {
                word-break: break-all; 
            }

            iframe {
                position: fixed;
                bottom: 0;
                z-index: 100;
            }

            .st-emotion-cache-8ijwm3 {
                height: 48px;
            }
        
            .stApp [data-testid="stToolbar"]{
                display:none;
            }
            
            .st-emotion-cache-qcqlej{
                display:none;
            }
            
            .block-container {
                padding: 2rem 1rem 10rem 1rem;
            }
            </style>
        """,
        unsafe_allow_html=True,
    )

    system_prompt = SystemMessage(content=global_prompt)

    dialog = [
        (
            "Меня уже трясет от вашего контакт-центра. Объясните, на основании какого закона ваши сотрудники сами прерывают связь?",
            "Сожалею, что произошла такая ситуация. Расскажите, что у Вас случилось?",
        ),
        (
            "Жалобу пишите давайте!!!",
            "Я искренне хочу Вам помочь 🙏! Расскажите, пожалуйста, с каким вопросом Вы обращались?",
        ),
        (
            "Не надо спрашивать, какой у меня вопрос! Пишите жалобу!!!",
            "Хорошо. Давайте сверим Вашу фамилию, имя, отчество и дату рождения. Назовите, пожалуйста.",
        ),
        (
            "Зачем? Вы не можете сами найти? ... Александров Александр Александрович, 15 мая 1980. Что еще вам там от меня нужно?!",
            "Спасибо, я прямо сейчас сообщу руководителю об этой ситуации, он примет все меры.",
        ),
        (
            "Лишите премии нерадивого! Я не хочу в следующий раз тратить столько время на вас. Информацию передали?",
            "Да, будьте уверены. Я желаю Вам помочь, с каким вопросом Вы обращались?",
        ),
        ("Нет, я уже все узнал. До свидания.", "Всего доброго!"),
    ][:3]

    if "initialized" not in st.session_state:
        st.session_state.chat = GigaChat(
            credentials=st.secrets["GIGAAUTH"],
            verify_ssl_certs=False,
            scope="GIGACHAT_API_CORP",
            model="GigaChat-Pro",
            temperature=0.01,
        )
        lite_model = GigaChat(
            credentials=st.secrets["GIGAAUTH"],
            scope="GIGACHAT_API_CORP",
            verify_ssl_certs=False,
            temperature=0.01,
        )
        st.session_state.semantic_sim_processor = semantic_sim.SemanticSimProcessor(
            model=st.session_state.chat, emb_secret=st.secrets["GIGAAUTH"]
        )
        st.session_state.typo_processor = typo.TypoProcessor(model=lite_model)

        # Send 'ready' signal to LMS
        html(
            """
                <script type="text/javascript">
                window.parent.parent.postMessage({status: 'ready'}, '*');
                var chat_container = parent.document.querySelector('.st-emotion-cache-0');
                chat_container.scrollTop = chat_container.scrollHeight;
                </script>
            """,
            height=0,
        )
        st.session_state.answer_index = 0
        st.session_state.initialized = True

    # Read custom tasks
    if "data" in st.query_params:
        st.session_state.dialog = eval(st.query_params["data"])
        dialog = st.session_state.dialog

    st.session_state.comment = st.query_params.get("comment")
    comment = st.session_state.comment

    # Chat init
    if "messages" not in st.session_state:
        assert len(dialog), "No tasks provided!"

        st.session_state.dialog_index = 0
        st.session_state.n_dialogs = len(dialog)
        st.session_state.next_dialog = dialog[0]

        st.session_state.messages = [
            {
                "role": "assistant",
                "avatar": "👨‍💼",
                "content_type": ["text"],
                "content": [st.session_state.next_dialog[constants.CLIENT_MSG_IND]],
            }
        ]
        st.session_state.show_input = True
        st.session_state.is_last_msg = False
        st.session_state.show_reset_button = False
        st.session_state.input_msg = None
        st.session_state.score = []

    if comment:
        st.markdown(comment)
    st.title("Тренажёр чата")
    # Chat cache
    for idx, msg_block in enumerate(st.session_state.messages, start=1):
        with st.chat_message(name=msg_block["role"], avatar=msg_block["avatar"]):
            for i, content_type in enumerate(msg_block["content_type"]):
                if content_type == "text":
                    st.write(msg_block["content"][i])
                elif content_type == "expand":
                    if (
                        st.session_state.show_reset_button
                        or st.session_state.is_last_msg
                    ):
                        if idx == len(st.session_state.messages) - (
                            len(st.session_state.messages) % 3
                        ):
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.button(
                                    "↻ Повтор",
                                    on_click=reset_last_msg,
                                    use_container_width=True,
                                )
                            with col2.expander(label=msg_block["content"][i][0]):
                                st.write(msg_block["content"][i][1])
                            st.session_state.show_reset_button = False
                    else:
                        with st.expander(label=msg_block["content"][i][0]):
                            st.write(msg_block["content"][i][1])

    # Main application loop
    if st.session_state.show_input:
        input_msg = st.session_state.input_msg
        if input_msg and input_msg.lstrip():
            with st.chat_message("user", avatar="👨‍🏫"):
                st.write(input_msg)
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "avatar": "👨‍🏫",
                        "content_type": ["text"],
                        "content": [input_msg],
                    }
                )

            with st.chat_message("assistant", avatar="🤖"):

                with st.spinner(text="Анализирую ваш ответ..."):
                    vals_in_res = 0
                    # --- Typo checking
                    typo_score, message_typo = st.session_state.typo_processor.run(
                        input_msg
                    )
                    vals_in_res += 1

                    input_msg = input_msg.lower()
                    # --- Semantic similarity checking
                    (semantic_score, found), message_semantic = (
                        st.session_state.semantic_sim_processor.run(
                            user_message=input_msg,
                            target_message=st.session_state.next_dialog[
                                constants.TARGET_MSG_IND
                            ],
                        )
                    )
                    vals_in_res += found

                    # --- Emoji checking
                    emoji_prompt = SystemMessage(
                        content="""Ты - тренеражер центра поддержки. Твоя цель: сформировать у сотрудника профессиональный навык написания ответов.\n\
                                    Оцени схожесть и уместность использования эмоджи в ответе [Сотрудник] сравнительно с [Верный ответ]. \n\
                                    Формат вывода: 1. Использование эмоджи: <комментарий>. Оценка: {0, 25, 50, 75, 100}%.
                                    """
                    )

                    res_emoji = None
                    emoji_in_msg = bool(emoji.distinct_emoji_list(input_msg))
                    emoji_in_target = bool(
                        emoji.distinct_emoji_list(
                            st.session_state.next_dialog[constants.TARGET_MSG_IND]
                        )
                    )

                    if emoji_in_msg and emoji_in_target:
                        prompt_content = f"{constants.TARGET_PREFIX} {st.session_state.next_dialog[constants.TARGET_MSG_IND]}\n\
                                           {constants.USER_PREFIX} {input_msg}"

                        prompt = [emoji_prompt, HumanMessage(content=prompt_content)]

                        res_emoji = st.session_state.chat(prompt).content

                        emoji_score = 0
                        # FIXME: Code duplication
                        try:  # Sometimes the response format may be incorrect
                            emoji_score += int(
                                "".join(
                                    list(
                                        filter(
                                            str.isdigit, res_emoji.split("Оценка: ")[-1]
                                        )
                                    )
                                )
                            )
                        except Exception as e:
                            emoji_score = (
                                0  # FIXME: think about how to deal with such cases
                            )
                    elif not emoji_in_msg and not emoji_in_target:
                        emoji_score = 100
                    elif not emoji_in_msg and emoji_in_target:
                        emoji_score = -1
                    else:
                        emoji_score = -2

                    vals_in_res += 1

                    # --- Main analysis
                    prompt_content = f"""
                        {constants.TARGET_PREFIX} {st.session_state.next_dialog[constants.TARGET_MSG_IND]}\n\
                        {constants.USER_PREFIX} {input_msg}
                    """

                    prompt = [system_prompt, HumanMessage(content=prompt_content)]

                    # Request PRO model
                    res_rest = st.session_state.chat(prompt).content
                    rest_score = 0
                    for x in res_rest.split("\n"):
                        score, found = score_parser.split_parse_score(
                            x, constants.SCORE_PATTERN
                        )
                        rest_score += score
                        vals_in_res += found

                if emoji_score == constants.MAX_SCORE_PER_TASK:
                    message_emoji = (
                        res_emoji
                        or "1. Использование эмоджи: Эмоджи не использовались. Оценка: 100%"
                    )
                elif emoji_score == 0:
                    message_emoji = res_emoji
                elif emoji_score == -1:
                    message_emoji = "1. Использование эмоджи: В данной ситуации предусмотрено использование эмоджи. Оценка: 0%"
                    emoji_score = 0
                elif emoji_score == -2:
                    message_emoji = "1. Использование эмоджи: В данной ситуации не предусмотрено использование эмоджи. Оценка: 0%"
                    emoji_score = 0
                else:
                    message_emoji = res_emoji

                target_expander = [
                    "Верный ответ",
                    dialog[st.session_state.dialog_index][constants.TARGET_MSG_IND],
                ]

                task_score = min(
                    round(
                        sum([rest_score, emoji_score, typo_score, semantic_score])
                        / vals_in_res
                    ),
                    constants.MAX_SCORE_PER_TASK,
                )
                st.session_state.score.append(task_score)
                score_message = f"{res_rest}\n\nБалл за ответ: {task_score}% из {constants.MAX_SCORE_PER_TASK}%\n\n"

                final_message = "\n".join(
                    [
                        constants.CHAT_PREFIX,
                        message_typo,
                        message_emoji,
                        message_semantic,
                        score_message,
                    ]
                )
                st.write(final_message)

                col1, col2 = st.columns([1, 3])
                with col1:
                    st.button(
                        "↻ Повтор", on_click=reset_last_msg, use_container_width=True
                    )
                with col2.expander(label=target_expander[0]):
                    st.write(target_expander[1])

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "avatar": "🤖",
                        "content_type": ["text", "expand"],
                        "content": [
                            final_message,
                            target_expander,
                        ],
                    }
                )

            st.session_state.answer_index += (
                1 if not st.session_state.answer_index else 3
            )
            st.session_state.dialog_index += 1

            if st.session_state.dialog_index < st.session_state.n_dialogs:
                st.session_state.next_dialog = dialog[st.session_state.dialog_index]

                with st.chat_message("assistant", avatar="👨‍💼"):
                    st.write(st.session_state.next_dialog[constants.CLIENT_MSG_IND])

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "avatar": "👨‍💼",
                        "content_type": ["text"],
                        "content": [
                            st.session_state.next_dialog[constants.CLIENT_MSG_IND]
                        ],
                    }
                )
            else:
                st.session_state.is_last_msg = True
                st.session_state.show_input = False
                st.rerun()  # To hide input bar

        # st.markdown('''<script>a = document.getElementsByClassName("st-emotion-cache-0"); console.log(a);</script>''', unsafe_allow_html=True)
        custom_input(disabled=False, key="input_msg")
        temp = st.empty()
        with temp:
            st.components.v1.html(js_scroll)
            time.sleep(0.5)
        temp.empty()

    if st.session_state.dialog_index >= st.session_state.n_dialogs:
        with st.chat_message("assistant", avatar="🤖"):
            percent_result = round(
                sum(st.session_state.score)
                / (len(st.session_state.score) * constants.MAX_SCORE_PER_TASK)
                * 100,
                2,
            )

            st.write("Задание завершено, спасибо!")
            st.markdown(
                f'<h1 align="center">Ваш балл: {percent_result}%</h1>',
                unsafe_allow_html=True,
            )

            html(
                f"""
                <script>
                    window.parent.parent.postMessage({{result: {[sum(st.session_state.score), len(st.session_state.score) * constants.MAX_SCORE_PER_TASK]}}}, "*");
                </script>
                    """,
                height=0,
            )
        temp = st.empty()
        with temp:
            st.components.v1.html(js_scroll)
            time.sleep(0.5)
        temp.empty()


except Exception as e:
    print(e)
    st.error("Internal server error")
    st.stop()
