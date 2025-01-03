from langchain.schema import HumanMessage, SystemMessage

from core.critique.common.parsers import score as score_parser
from core.lib import constants

system_prompt = """
    Ты - тренажёр чата поддержки. 
    Оцени красочность текста сотрудника - Присутствуют ли в ответе слова-паразиты? Красочна или бедна речь? Грамотно ли построена фраза? Пременены слишком сложные обороты или термины?
    
    <Комментарий> - твой комментарий, как эксперта.
    [Сотрудник] - распознанный голосовой ответ сотрудника, его надо оценить.
    [Верный ответ] - сотрудник должен ответить похожим образом.
    Если ответ сотрудника соотвествует верному ответу - оценка 100.
    Игнорируй грамматические ошибки.

    <Оценка> - выбери одно из значений {0, 25, 50, 75, 100}.

    Убедись, что ответ написан в следующем формате, сохраняя нумерацию пунктов:

    1. Красочность речи: <Комментарий>. Оценка - <Оценка>%.
"""


class EloquenceProcessor:
    def __init__(self, model):
        self.model = model

    def run(self, context: str):

        asr_response = context.service_result.texts[0]
        right_answer = context.current_task.right_answer

        prompt = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"""
                        {constants.TARGET_PREFIX} {right_answer}
                        {constants.USER_PREFIX} {asr_response}
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

            if not score_parser_response[1]:
                raise constants.GenerationError
        
            score += score_parser_response[0]
            n_found += score_parser_response[1]

        return score, response, n_found
