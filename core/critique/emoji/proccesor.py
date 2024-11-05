from langchain.schema import SystemMessage, HumanMessage
from langchain.chat_models.gigachat import GigaChat
from core.critique.emoji.prompts import emoji_prompt
from core.critique.common.parsers import score as score_parser
import constants
from dataclasses import dataclass, field
import emoji
import re

EMPTY_STR = ""
SEP = " "


@dataclass
class EmojiConfig: ...


class EmojiProcessor:
    def __init__(self, model: GigaChat):
        self.model = model
        self.config = EmojiConfig()

    def has_emoji(self, text: str) -> bool:
        return bool(emoji.distinct_emoji_list(text))

    def run(self, user_message: str, target_message: str):
        emoji_in_msg = self.has_emoji(user_message)
        emoji_in_target = self.has_emoji(target_message)

        if emoji_in_msg:
            sys_prompt = SystemMessage(content=emoji_prompt)

            prompt_content = HumanMessage(
                content=f"""
                    {constants.TARGET_PREFIX} {target_message}
                    {constants.USER_PREFIX} {user_message}
                """
            )

            prompt = [sys_prompt, prompt_content]

            response = self.model(prompt).content

            score_parser_responce = score_parser.split_parse_score(
                response, constants.SCORE_PATTERN
            )

            if not score_parser_responce[1]:
                response + "Оценка: 0%."
                score_parser_responce[1] = 1

            return score_parser_responce, response

        elif not emoji_in_msg and not emoji_in_target:
            emoji_score = 100
            response = "1. Использование эмоджи: Эмоджи не использовались. Оценка: 100%"
        else:
            emoji_score = 0
            response = "1. Использование эмоджи: В данной ситуации предусмотрено использование эмоджи. Оценка: 0%"

        return (emoji_score, 1), response
