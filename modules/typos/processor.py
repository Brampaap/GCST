import re
from langchain.schema import SystemMessage
from langchain.chat_models.gigachat import GigaChat
from modules.typos.promts import typo_system_prompt_template
from constants import MAX_SCORE_PER_TASK, SEP
from Levenshtein import distance as levenshtein_dist
import emoji
from dataclasses import dataclass, field


@dataclass
class TypoConfig:
    max_diff: int = field(default=5)


class TypoProcessor:
    replacemets = {
        "ё": "е",
        " .": ".",
        " !": "!",
        " ?": "?",
    }

    def __init__(self, model: GigaChat):
        self.model = model
        self.config = TypoConfig()

    @classmethod
    def clean_message(cls, user_message):

        user_message = re.sub(r"[\U0001fa75]", "", user_message)
        user_message = emoji.replace_emoji(user_message, replace="").strip()
        user_message = re.sub(r"\s+", " ", user_message)

        for x, y in cls.replacemets.items():
            user_message = user_message.replace(x, y)

        user_message = (
            user_message[:-1] if user_message[-1] in ["!", "."] else user_message
        )

        return user_message

    def highlight_diff(self, lstr, rstr):
        # TODO: Add word position accounting
        rwords = set(rstr.split(SEP))
        lwords = set(lstr.split(SEP))

        rstr = SEP.join(
            [f":green[{x}]" if x not in lwords else x for x in rstr.split(SEP)]
        )
        lstr = SEP.join(
            [f":red[{x}]" if x not in rwords else x for x in lstr.split(SEP)]
        )
        return lstr, rstr

    def compute_score(self, lstr, rstr) -> int:
        score = max(self.config.max_diff - levenshtein_dist(lstr, rstr), 0)
        score *= MAX_SCORE_PER_TASK / self.config.max_diff
        return int(score)

    def prepare_response(self, lstr, rstr, score):
        lstr, rstr = self.highlight_diff(lstr, rstr)

        if score == MAX_SCORE_PER_TASK:
            response_message = "1. Грамматика: Ошибок нет. Оценка: 100%"
        else:
            response_message = f'1. Грамматика: Найдены опечатки: "{lstr}"; \nИсправленное сообщение: "{rstr}". \nОценка: {score}%'

        return response_message

    def run(self, user_message: str):
        user_message = self.clean_message(user_message)

        prompt = [
            SystemMessage(
                content=typo_system_prompt_template.substitute(
                    typo_input_msg=user_message
                )
            )
        ]

        response = self.model(prompt).content
        response = self.clean_message(response)

        score = self.compute_score(user_message, response)

        response_message = self.prepare_response(user_message, response, score)

        return score, response_message
