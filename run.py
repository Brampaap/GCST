import streamlit as st
import time
import html
from streamlit.components.v1 import html as html_st
import streamlit.components.v1 as components
from tests.test_service_mock import service
# TODO: сократить импорты
from core.critique.typos import processor as typo
from core.critique.semantic import proccesor as semantic_sim
from core.critique.emoji import proccesor as emoji_proc
from core.critique.common.prompt import global_prompt
from core.critique.common.parsers import score as score_parser
import constants
from core.lib.exercise.default import dialog


from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

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
    custom_input = components.declare_component("custom_input", path="build") #url="http://localhost:3000")

    def render_no_copy_text(text: str) -> str:
        rendered = f"""
        <div class="text-container">
            <div class="overlay"></div>
            <div class="no-select-text">
                <p>{html.escape(text)}</p>
            </div>  
        </div>"""

        return rendered

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
            .text-container {
                position: relative;
                display: inline-block;
                width: 100%;
            }

            .overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: transparent;
                z-index: 10;
            }

            .no-select-text {
                pointer-events: none;
            }

            .no-select-text > p {
                -webkit-user-select: none; /* Safari */
                -moz-user-select: none;
                -ms-user-select: none;
                user-select: none;
            }

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
        st.session_state.emoji_processor = emoji_proc.EmojiProcessor(
            model=st.session_state.chat
        )

        # Send 'ready' signal to LMS
        html_st(
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
                                st.markdown(
                                    render_no_copy_text(msg_block["content"][i][1]),
                                    unsafe_allow_html=True,
                                )
                            st.session_state.show_reset_button = False
                    else:
                        with st.expander(label=msg_block["content"][i][0]):
                            st.markdown(
                                render_no_copy_text(msg_block["content"][i][1]),
                                unsafe_allow_html=True,
                            )

    # Main application loop
    if st.session_state.show_input:
        
        input_msg = st.session_state.input_msg
        if input_msg:
            with st.chat_message("user", avatar="👨‍🏫"):
                with st.spinner(text="Распознавание..."):
                    asr_responce = service.process(input_msg)
                    st.write(asr_responce)
                    st.session_state.messages.append(
                        {
                            "role": "user",
                            "avatar": "👨‍🏫",
                            "content_type": ["text"],
                            "content": [asr_responce],
                        }
                    )

            with st.chat_message("assistant", avatar="🤖"):

                with st.spinner(text="Анализирую ваш ответ..."):
                    vals_in_res = 0
                    # --- Typo checking
                    # typo_score, message_typo = st.session_state.typo_processor.run(
                    #     asr_responce
                    # )
                    typo_score = 100
                    message_typo = "Результат"
                    vals_in_res += 1

                    asr_responce = asr_responce.lower()
                    # --- Semantic similarity checking
                    # (semantic_score, found), message_semantic = (
                    #     st.session_state.semantic_sim_processor.run(
                    #         user_message=asr_responce,
                    #         target_message=st.session_state.next_dialog[
                    #             constants.TARGET_MSG_IND
                    #         ],
                    #     )
                    # )
                    (semantic_score, found), message_semantic = (100, True), "Всё хорошо!"
                    vals_in_res += found

                    # --- Emoji checking
                    (emoji_score, found), message_emoji = (
                        st.session_state.emoji_processor.run(
                            user_message=asr_responce,
                            target_message=st.session_state.next_dialog[
                                constants.TARGET_MSG_IND
                            ],
                        )
                    )
                    vals_in_res += found

                    # --- Main analysis
                    prompt_content = f"""
                        {constants.TARGET_PREFIX} {st.session_state.next_dialog[constants.TARGET_MSG_IND]}\n\
                        {constants.USER_PREFIX} {asr_responce}
                    """

                    prompt = [system_prompt, HumanMessage(content=prompt_content)]

                    # Request PRO model
                    res_rest = "Результат" #st.session_state.chat(prompt).content
                    rest_score = 0
                    for x in res_rest.split("\n"):
                        score, found = score_parser.split_parse_score(
                            x, constants.SCORE_PATTERN
                        )
                        rest_score += score
                        vals_in_res += found

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
                    st.markdown(
                        render_no_copy_text(target_expander[1]), unsafe_allow_html=True
                    )

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

        custom_input(key="input_msg")
        temp = st.empty()
        with temp:
            html_st(js_scroll)
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

            html_st(
                f"""
                <script>
                    window.parent.parent.postMessage({{result: {[sum(st.session_state.score), len(st.session_state.score) * constants.MAX_SCORE_PER_TASK]}}}, "*");
                </script>
                    """,
                height=0,
            )
        temp = st.empty()
        with temp:
            html_st(js_scroll)
            time.sleep(0.5)
        temp.empty()


except Exception as e:
    print(e)
    st.error("Internal server error")
    st.stop()
