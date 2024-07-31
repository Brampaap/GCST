import streamlit as st
import time
from streamlit.components.v1 import html
import streamlit.components.v1 as components

from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
from Levenshtein import distance
import emoji
import re

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

    system_prompt = SystemMessage(
        content='\
    Ты - тренеражер центра поддержки. Твоя цель: сформировать у сотрудника профессиональный навык написания ответов.\n\
    Оцени последний ответ сотрудника по всем пунктам:\n\
    1. Смысловая схожесть: Сравни ответ сотрудника с верным ответом на предмет семантической схожести.\n\
    2. Клиентоориентированность: Оцени уровень сервиса в ответе сотрудника, какого общее впечатление от обращения к клиенту.\n\
    3. Понятность текста: Оцени логическую структуру и ясность ответа сотрудника. Насколько легко текст может быть понят клиентом.\n\
    \n\
    По каждому пункту напиши короткий <Комментарий> и поставь <Оценка> = {0, 25, 50, 75, 100}: "<Имя пункта>: <Комментарий>. Оценка: <Оценка>%."'
    )

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

    CLIENT_MSG_IND = 0
    TARGET_MSG_IND = 1
    N_CRITERIONS = 5
    MAX_TYPOS = 4
    MAX_SCORE_PER_TASK = 100

    USER_PREFIX = "[Сотрудник]"
    TARGET_PREFIX = "[Верный ответ]"
    CLIENT_PREFIX = "[Клиент]"
    CHAT_PREFIX = "[Оценка ответа]"

    if "initialized" not in st.session_state:
        st.session_state.chat = GigaChat(
            credentials=st.secrets["GIGAAUTH"],
            verify_ssl_certs=False,
            scope="GIGACHAT_API_CORP",
            model="GigaChat-Pro",
        )
        st.session_state.chat_lite = GigaChat(
            credentials=st.secrets["GIGAAUTH"],
            scope="GIGACHAT_API_CORP",
            verify_ssl_certs=False,
        )

        # Send 'ready' signal to LMS
        html(
            """
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
                "content": [st.session_state.next_dialog[CLIENT_MSG_IND]],
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

    def get_string_diff(lstr, rstr):
        rwords = set(rstr.split(" "))
        lwords = set(lstr.split(" "))

        rstr = " ".join(
            [f":green[{x}]" if x not in lwords else x for x in rstr.split(" ")]
        )
        lstr = " ".join(
            [f":red[{x}]" if x not in rwords else x for x in lstr.split(" ")]
        )
        return lstr, rstr

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
                    # Typo checking
                    typo_input_msg = "".join(x for x in input_msg if not emoji.is_emoji(x)).strip()
                    print(typo_input_msg)
                    typo_prompt = [
                        HumanMessage(
                            content=f"Перепиши текст, исправив грамматические, орфографические и пунктуационные ошибки в тексте.\nТекст: {typo_input_msg}\nИсправленный текст:"
                        )
                    ]
                    # Request LITE model
                    res_typo = st.session_state.chat_lite(typo_prompt).content
                    typo_score = max(MAX_TYPOS - distance(typo_input_msg, res_typo), 0)
                    typo_score *= MAX_SCORE_PER_TASK // MAX_TYPOS

                    lstr_typo, rstr_typo = get_string_diff(typo_input_msg, res_typo)

                    # Emoji checking
                    emoji_prompt = SystemMessage(
                        content="""Ты - тренеражер центра поддержки. Твоя цель: сформировать у сотрудника профессиональный навык написания ответов.\n\
                                    Оцени схожесть и уместность использования эмоджи в ответе [Сотрудник] сравнительно с [Верный ответ]. \n\
                                    Формат вывода: 1. Использование эмоджи: <комментарий>. Оценка: {0, 25, 50, 75, 100}%.
                                    """
                    )
                    
                    res_emoji = None
                    emoji_in_msg = bool(emoji.distinct_emoji_list(input_msg))
                    emoji_in_target = bool(emoji.distinct_emoji_list(st.session_state.next_dialog[TARGET_MSG_IND]))
                        
                    if emoji_in_msg and emoji_in_target:
                        prompt_content = f"{TARGET_PREFIX} {st.session_state.next_dialog[TARGET_MSG_IND]}\n\
                                           {USER_PREFIX} {input_msg}"

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

                    # Main analysis
                    prompt_content = f"{CLIENT_PREFIX} {st.session_state.next_dialog[CLIENT_MSG_IND]}\n\
                                {TARGET_PREFIX} {st.session_state.next_dialog[TARGET_MSG_IND]}\n\
                                {USER_PREFIX} {input_msg}\
                                "

                    prompt = [system_prompt, HumanMessage(content=prompt_content)]

                    # Request PRO model
                    res_rest = st.session_state.chat(prompt).content

                    rest_score = 0
                    try:  # Sometimes the response format may be incorrect
                        for x in res_rest.split("\n"):
                            rest_score += int(
                                "".join(
                                    list(filter(str.isdigit, x.split("Оценка: ")[-1]))
                                )
                            )
                    except Exception as e:
                        rest_score = 0  # FIXME: think about how to deal with such cases

                task_score = min(
                    round((rest_score + emoji_score + typo_score) / N_CRITERIONS), MAX_SCORE_PER_TASK
                )
                st.session_state.score.append(task_score)

                chat_response = f"{res_rest}\n\nБалл за ответ: {task_score}% из {MAX_SCORE_PER_TASK}%\n\n"

                if typo_score == MAX_SCORE_PER_TASK:
                    message_typo = "1. Грамматика: Ошибок нет. Оценка: 100%"
                else:
                    message_typo = f'1. Грамматика: Найдены опечатки: "{lstr_typo}"; \nИсправленное сообщение: "{rstr_typo}". \nОценка: {typo_score}%'

                if emoji_score == MAX_SCORE_PER_TASK:
                    message_emoji = (
                        res_emoji
                        or "1. Использование эмоджи: Эмоджи не использовались. Оценка: 100%"
                    )
                elif emoji_score == 0:
                    message_emoji = res_emoji
                elif emoji_score == -1:
                    message_emoji = "1. Использование эмоджи: В данной ситуации предусмотрено использование эмоджи. Оценка: 0%"
                elif emoji_score == -2:
                    message_emoji = "1. Использование эмоджи: В данной ситуации не предусмотрено использование эмоджи. Оценка: 0%"
                else:
                    message_emoji = res_emoji

                target_expander = [
                    "Верный ответ",
                    dialog[st.session_state.dialog_index][TARGET_MSG_IND],
                ]

                st.write(
                    f"{CHAT_PREFIX}\n{message_typo}\n{message_emoji}\n{chat_response}"
                )
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
                            f"{CHAT_PREFIX}\n{message_typo}\n{message_emoji}\n{chat_response}",
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
                    st.write(st.session_state.next_dialog[CLIENT_MSG_IND])

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "avatar": "👨‍💼",
                        "content_type": ["text"],
                        "content": [st.session_state.next_dialog[CLIENT_MSG_IND]],
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
                / (len(st.session_state.score) * MAX_SCORE_PER_TASK)
                * 100,
                2,
            )

            st.write("Задание завершено, спасибо!")
            st.markdown(
                f'<h1 align="center">Ваш балл: {sum(st.session_state.score)}/{len(st.session_state.score) * MAX_SCORE_PER_TASK}\n\n({percent_result}%)</h1>',
                unsafe_allow_html=True,
            )
            
            
            html(
                f"""
                <script>
                    window.parent.parent.postMessage({{result: {[sum(st.session_state.score), len(st.session_state.score) * MAX_SCORE_PER_TASK]}}}, "*");
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
