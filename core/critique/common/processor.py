from langchain.schema import HumanMessage, SystemMessage

from core.critique.common.parsers import score as score_parser
from core.lib import constants

system_prompt = """
    Ты - тренеражер центра поддержки. 
    Сотрудник должен с уважением отвечать клиенту. При обращение сотрудника к клиенту, проследни, что он говорит с ним на "вы".
    Ты профессионал по оценке следующих пунктов:
    - Клиентоориентированность: Уровень сервиса и вежливости в ответе сотрудника. Насколько уважительным было обращение к клиенту?
    - Понятность текста: Логическая структура и ясность ответа сотрудника. Насколько легко текст может быть понят клиентом?

    <Оценка> - выбери одно из значений {0, 25, 50, 75, 100}
    <Комментарий> - твой комментарий, как эксперта. Когда Оценка: 100, <Комментарий> должен быть не более трёх слов.
    [Сотрудник] - ответ сотрудника, его надо оценить.
    [Верный ответ] - опирайся на этот вопрос текст, похожим образом должен ответить сотрудник.

    Убедись, что ответ написан в следующем формате, сохраняя нумерацию пунктов:

    1. Клиентоориентированность: <Комментарий>. Оценка: <Оценка>%.
    2. Понятность текста: <Комментарий>. Оценка: <Оценка>%.
"""


class ССSProcessor:
    """Сlient Сentric And Structure"""

    def __init__(self, model):
        self.model = model

    def run(self, context: str):

        right_answer = context.current_task.right_answer
        asr_response = context.asr_response

        prompt = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"""
                        {constants.TARGET_PREFIX}\\s{right_answer}\n\n
                        {constants.USER_PREFIX}\\s{asr_response}
                        """
            ),
        ]

        response = self.model(prompt).content

        score = 0
        n_found = 0
        for task in response.split(constants.LF):
            score_parser_response = score_parser.split_parse_score(
                task, constants.SCORE_PATTERN
            )
            score += score_parser_response[0]
            n_found += score_parser_response[1]

        return score, response, n_found
