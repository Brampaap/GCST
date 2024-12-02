from langchain.schema import HumanMessage, SystemMessage

from core.critique.common.parsers import score as score_parser
from core.lib import constants

system_prompt = """
    Ты - лояльный тренажёр чата поддержки. 
    Оцени клиентоориентированность - это уровень сервиса и вежливости в ответе сотрудника. Насколько уважительным было обращение к клиенту?

    <Комментарий> - твой комментарий, как эксперта.
    [Верный ответ] - сотрудник должен ответить похожим образом.
    [Сотрудник] - распознанный голосовой ответ сотрудника, его надо оценить.
    Если ответ сотрудника соотвествует верному ответу - оценка 100.

    <Оценка> - выбери одно из значений {0, 25, 50, 75, 100}.

    Убедись, что ответ написан в следующем формате, сохраняя нумерацию пунктов:

    1. Клиентоориентированность: <Комментарий>. Оценка: <Оценка>%.
"""


class ССSProcessor:
    """Сlient Сentric And Structure"""

    def __init__(self, model):
        self.model = model

    def run(self, context: str):

        right_answer = context.current_task.right_answer
        asr_response = context.service_result.texts[0]

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
