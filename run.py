import streamlit as st

from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat 

st.markdown('''
<style>
.stApp [data-testid="stToolbar"]{
    display:none;
}
</style>
''', unsafe_allow_html=True)

chat = GigaChat(
    credentials=st.secrets["GIGAAUTH"],
    verify_ssl_certs=False,
    model="GigaChat-Pro",
)

prompts = [
    SystemMessage(
        content='\
Ты инструктор колл-центра с опытом более 10 лет.\n\
Оцени ответ [Сотрудник] на запрос [Клиент], зная правильны ответ [Эталон] по критериям:\n\
1. Граматические ошибки: Определи грамматические ошибки в ответе [Сотрудник]\n\
2. Смысловая схожесть: Сравни ответ сотрудника с эталоном.\n\
3. Клиентоориентированность: Оцени уровень сервиса в ответе сотрудника. Обрати внимание на общее впечатление от обращения к клиенту. Обращение на "ты" считается асолютно недопустимым.\n\
4. Использование эмоджи: Проанализируй использование эмоджи только в ответе сотрудника. {Уместно. Оценка: 1 / Отсутствие/Неуместно. Оценка: 0} \n\
5. Понятность текста: Оцени структуру и ясность ответа в ответе сотрудника. Проверь, насколько легко текст может быть понят клиенту.\n\
Каждому пункту должна соответствовать численная оценка от 1 до 5, где 5 означает отличное соответствие стандартам, а 1 — значительное отклонение.\n\
Обоснуй каждую оценку, указывая конкретные примеры из текста.\n\
\n\
В самом конце предоставь итог с рекомендациями для улучшения текущего ответа сотрудника.\n\
Общая возможная сумма баллов = 21.\
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
user_prefix = "[Сотрудник]"
reference_prefix = "[Эталон]"
client_prefix = "[Клиент]"
trainer_prefix = "[Система]"

# Chat init
if "messages" not in st.session_state:
    st.session_state.curr_answer = 0
    st.session_state.messages = []
    st.session_state.next_content = dialog[st.session_state.curr_answer]
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content_type": ["text"],
            "content": [st.session_state.next_content][client_idx],
        }
    )

    st.session_state.prompts = prompts
    st.session_state.n_answers = len(dialog)

st.title("Интеллектуальный тренажер для сотрудников")

# Cache
for x in st.session_state.messages:
    with st.chat_message(x["role"]):
        for i, content_type in enumerate(x["content_type"]):
            if content_type == "text":
                st.write(x["content"][i])
            elif content_type == "expand":
                with st.expander(x["content"][i][0]):
                    st.write(st.write(x["content"][i][1]))

# Main application loop
if st.session_state.curr_answer < st.session_state.n_answers:
    if content := st.chat_input("Ваш ответ:"):
        with st.chat_message("user"):
            st.write(content)
            st.session_state.messages.append(
                {"role": "user", "content_type": ["text"], "content": [content]}
            )

        prompt = f"{client_prefix} {st.session_state.next_content[client_idx]}\n\
                    {reference_prefix} {st.session_state.next_content[target_idx]}\n\
                    {user_prefix} {content}\n\
                    "
        st.session_state.prompts.append(HumanMessage(content=prompt))

        with st.chat_message("assistant"):
            res = chat(st.session_state.prompts).content
            answer, rep_part = res.split('Итоговая оценка')
            st.write(f"{trainer_prefix}\n{answer}")

            report = ["Дополнительная рекомендация", f"Итоговая оценка {rep_part}",]
            target = [
                "Эталонный ответ",
                dialog[st.session_state.curr_answer][target_idx],
            ]
            with st.expander(report[0]):
                st.write(report[1])
            with st.expander(target[0]):
                st.write(target[1])
        
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content_type": ["text", "expand", "expand"],
                    "content": [f"{trainer_prefix}\n{answer}", target, report],
                }
            )

        # Clean conversation history
        st.session_state.prompts = st.session_state.prompts[:-1]

        # Write next task
        st.session_state.curr_answer += 1
        if st.session_state.curr_answer < st.session_state.n_answers:
            st.session_state.next_content = dialog[st.session_state.curr_answer]

            with st.chat_message("assistant"):
                st.write(st.session_state.next_content[client_idx])

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content_type": ["text"],
                    "content": [st.session_state.next_content[client_idx]],
                }
            )

    if st.session_state.curr_answer > 0 and st.button("↻ Повторить задание"):
        st.session_state.curr_answer -= 1
        st.session_state.next_content = dialog[st.session_state.curr_answer]
        with st.chat_message("assistant"):
            st.write(st.session_state.next_content[client_idx])

        st.session_state.messages = st.session_state.messages[:-3]
        st.rerun()

else:
    st.write("Задание завершено, спасибо!")
    if st.button("↻ Повторить задание"):
        st.session_state.curr_answer -= 1
        st.session_state.next_content = dialog[st.session_state.curr_answer]
        with st.chat_message("assistant"):
            st.write(st.session_state.next_content[client_idx])

        st.session_state.messages = st.session_state.messages[:-2]
        st.rerun()
