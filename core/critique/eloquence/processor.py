from langchain.schema import HumanMessage, SystemMessage

from core.critique.common.parsers import score as score_parser
from core.lib import constants

system_prompt = """
    Ты - лояльный тренажёр чата поддержки. 
    Оцени красочность текста сотрудника - Присутствуют ли в ответе слова-паразиты? Красочна или бедна речь? Грамотно ли построена фраза? Пременены слишком сложные обороты или термины?
    
    <Комментарий> - твой комментарий, как эксперта.
    [Сотрудник] - распознанный голосовой ответ сотрудника, его надо оценить.
    Игнорируй грамматические ошибки.

    <Оценка> - выбери одно из значений {0, 25, 50, 75, 100}.

    Убедись, что ответ написан в следующем формате, сохраняя нумерацию пунктов:

    1. Красочность речи: <Комментарий>. Оценка: <Оценка>%.
"""


class EloquenceProcessor:
    def __init__(self, model):
        self.model = model

    def run(self, context: str):

        asr_response = context.service_result.texts[0]

        prompt = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"""
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
