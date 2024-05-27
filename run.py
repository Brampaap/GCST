import os
import streamlit as st
from streamlit.components.v1 import html

from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
from Levenshtein import distance
try:
    st.markdown(
        """
    <style>
    .stApp [data-testid="stToolbar"]{
        display:none;
    }
    .st-emotion-cache-qcqlej{
        display:none;
    }
    
    </style>
    """,
        unsafe_allow_html=True,
    )
    
    chat = GigaChat(
        credentials="test",
        verify_ssl_certs=False,
        model="GigaChat-Pro",
    )
    chat_lite = GigaChat(
        credentials=os.environ["GIGAAUTH"],
        verify_ssl_certs=False,
    )
    prompts = [
        SystemMessage(
            content='\
    Ты инструктор колл-центра с опытом более 10 лет.\n\
    Оцени ответ [Сотрудник] на запрос [Клиент], зная правильны ответ [Эталон] по критериям:\n\
    1. Смысловая схожесть: Сравни ответ сотрудника с эталоном.\n\
    2. Клиентоориентированность: Оцени уровень сервиса в ответе сотрудника. Обрати внимание на общее впечатление от обращения к клиенту. Обращение на "ты" считается асолютно недопустимым.\n\
    3. Использование эмоджи: Проанализируй использование эмоджи только в ответе сотрудника. {Уместно. Оценка: 1 / Отсутствие/Неуместно. Оценка: 0} \n\
    4. Понятность текста: Оцени структуру и ясность ответа в ответе сотрудника. Проверь, насколько легко текст может быть понят клиенту.\n\
    Каждому пункту, кроме "Использование эмоджи", должна соответствовать численная оценка от 0 до 5, где 5 означает отличное соответствие стандартам, а 0 — значительное отклонение.\n\
    Обоснуй каждую оценку, указывая конкретные примеры из текста.\n\
    \n\
    В самом конце предоставь итог с рекомендациями для улучшения текущего ответа сотрудника.\n\
    Итог начинай фразой "Итоговая оценка: X из 16.\nРекомендация:"\
    '
        )
    ]
    
    dialog = [
        (
            "Меня уже трясет от вашего контакт-центра. Объясните, на основании какого закона ваши сотрудники сами прерывают связь?",
            "Сожалею, что произошла такая ситуация. Расскажите, что у Вас случилось?",
        ),
        (
            "Жалобу пишите давайте!!!",
            "Я искренне хочу Вам помочь! Расскажите, пожалуйста, с каким вопросом Вы обращались?",
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
    ]
    client_idx = 0
    target_idx = 1
    max_score_per_task = 21
    user_prefix = "[Сотрудник]"
    reference_prefix = "[Эталон]"
    client_prefix = "[Клиент]"
    trainer_prefix = "[Система]"
    
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.data_received = False
        html(
            """
                <script>
                window.parent.parent.postMessage({status: 'ready'}, '*');
                </script>
            """,
            height=0,
        )
    
    if "data" in st.query_params:
        st.session_state.dialog = eval(st.query_params["data"])
        st.session_state.data_received = True
        dialog = st.session_state.dialog
    
    
    # Chat init
    if "messages" not in st.session_state:
        st.session_state.curr_answer = 0
        st.session_state.messages = []
        st.session_state.next_content = dialog[st.session_state.curr_answer]
        st.session_state.messages.append(
            {
                "role": "assistant",
                "avatar": "👩‍🏫",
                "content_type": ["text"],
                "content": [st.session_state.next_content][client_idx],
            }
        )
        st.session_state.prompts = prompts
        st.session_state.n_answers = len(dialog) # min(len(dialog), 3)
        st.session_state.final_score = []
        st.session_state.disabled = False
        st.session_state.data_received = False
    
    placeholder = st.empty()
    st.title("Интеллектуальный тренажер для сотрудников")
    
    # Cache
    for x in st.session_state.messages:
        with st.chat_message(name=x["role"], avatar=x["avatar"]):
            for i, content_type in enumerate(x["content_type"]):
                if content_type == "text":
                    st.write(x["content"][i])
                elif content_type == "expand":
                    with st.expander(x["content"][i][0]):
                        st.write(x["content"][i][1])
    
    
    def get_string_diff(lstr, rstr):
        rwords = set(rstr.split(" "))
        lwords = set(lstr.split(" "))
    
        rstr = " ".join([f":green[{x}]" if x not in lwords else x for x in rstr.split(" ")])
        lstr = " ".join([f":red[{x}]" if x not in rwords else x for x in lstr.split(" ")])
        return lstr, rstr
    
    
    def disable():
        st.session_state["disabled"] = True
    
    
    # Main application loop
    if st.session_state.curr_answer < st.session_state.n_answers:
        if content := st.chat_input(
            "Ваш ответ:", disabled=st.session_state.disabled, on_submit=disable
        ):
            if content.lstrip():
                with st.chat_message("user", avatar="🙂"):
                    st.write(content)
                    st.session_state.messages.append(
                        {
                            "role": "user",
                            "avatar": "🙂",
                            "content_type": ["text"],
                            "content": [content],
                        }
                    )
    
                with st.chat_message("assistant", avatar="👩‍🏫"):
                    prompts_typo = [
                        HumanMessage(
                            content=f"Перепиши текст, исправив грамматические, орфографические и пунктуационные ошибки в тексте.\nТекст: {content}\nИсправленный текст:"
                        )
                    ]
    
                    with st.spinner(text="Анализирую ваш ответ..."):
                        # Type checking
                        res_typo = chat_lite(prompts_typo).content
                        typo_score = 5 - min(distance(content, res_typo), 5)
    
                        prompt = f"{client_prefix} {st.session_state.next_content[client_idx]}\n\
                                    {reference_prefix} {st.session_state.next_content[target_idx]}\n\
                                    {user_prefix} {content}\
                                    "
    
                        st.session_state.prompts.append(HumanMessage(content=prompt))
                        # Main analysis
                        res = chat(st.session_state.prompts).content
                        try:
                            answer, rep_part = res.split("Итоговая оценка:")
                        except ValueError:
                            answer = res
                            rep_part = " 0 "
    
                    task_score = min(int(rep_part[:3]) + typo_score, 21)
    
                    answer = f"{answer}\n\nИтоговая оценка: {task_score} из {max_score_per_task}.\n\n"
                    st.session_state.final_score.append(task_score)
    
                    rep_part = rep_part[10:]
                    lstr_typo, rstr_typo = get_string_diff(content, res_typo)
                    if typo_score == 5:
                        message_typo = "Оценка Грамматики: Ошибок нет. Оценка: 5/5."
                    else:
                        message_typo = f'Оценка Грамматики: Найдены опечатки.\n\nИсходное сообщение: "{lstr_typo}";\n\nИсправленное сообщение: "{rstr_typo}".\n\nОценка: {typo_score}/5.'
    
                    st.write(f"{trainer_prefix}\n{message_typo}\n{answer}")
    
                    report = [
                        "Дополнительная рекомендация",
                        rep_part,
                    ]
                    target = [
                        "Эталонный ответ",
                        dialog[st.session_state.curr_answer][target_idx],
                    ]
                    with st.expander(target[0]):
                        st.write(target[1])
                    if report[1]:
                        with st.expander(report[0]):
                            st.write(report[1])
    
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "avatar": "👩‍🏫",
                            "content_type": ["text", "expand"],
                            "content": [
                                f"{trainer_prefix}\n\n{message_typo}\n\n{answer}",
                                target,
                            ],
                        }
                    )
                    if report[1]:
                        st.session_state.messages[-1]["content_type"].append("expand")
                        st.session_state.messages[-1]["content"].append(report)
    
                # Clean conversation history
                st.session_state.prompts = st.session_state.prompts[:-1]
    
                # Write next task
                st.session_state.curr_answer += 1
                if st.session_state.curr_answer < st.session_state.n_answers:
                    st.session_state.next_content = dialog[st.session_state.curr_answer]
    
                    with st.chat_message("assistant", avatar="👩‍🏫"):
                        st.write(st.session_state.next_content[client_idx])
    
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "avatar": "👩‍🏫",
                            "content_type": ["text"],
                            "content": [st.session_state.next_content[client_idx]],
                        }
                    )
                st.session_state["disabled"] = False
                st.rerun()
    
        if st.session_state.curr_answer > 0 and st.button("↻ Повторить задание"):
            st.session_state.curr_answer -= 1
    
            st.session_state.next_content = dialog[st.session_state.curr_answer]
            with st.chat_message("assistant", avatar="👩‍🏫"):
                st.write(st.session_state.next_content[client_idx])
    
            st.session_state.messages = st.session_state.messages[:-3]
            st.session_state.final_score = st.session_state.final_score[:-1]
            st.rerun()
    
    else:
        st.write("Задание завершено, спасибо!")
        percent_result = round(
            sum(st.session_state.final_score)
            / (len(st.session_state.final_score) * max_score_per_task)
            * 100,
            2,
        )
        st.markdown(
            f'<h1 align="center">Ваш балл: {sum(st.session_state.final_score)}/{len(st.session_state.final_score) * max_score_per_task}\n\n({percent_result}%)</h1>',
            unsafe_allow_html=True,
        )
        html(
                f"""
            <script>
                window.parent.parent.postMessage({{result: {[sum(st.session_state.final_score), len(st.session_state.final_score) * max_score_per_task]}}}, "*")
            </script>
                """,
            height=0)
        if st.button("↻ Повторить задание"):
            st.session_state.curr_answer -= 1
            st.session_state.next_content = dialog[st.session_state.curr_answer]
            with st.chat_message("assistant", avatar="👩‍🏫"):
                st.write(st.session_state.next_content[client_idx])
    
            st.session_state.messages = st.session_state.messages[:-2]
            st.session_state.final_score = st.session_state.final_score[:-1]
            
            st.rerun()

except Exception as e:
    st.error("Internal server error")
    st.stop()
