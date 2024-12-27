import re
from dataclasses import dataclass, field

import numpy as np
from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.embeddings import GigaChatEmbeddings

from core.critique.common.parsers import score as score_parser
from core.critique.semantic.prompts import semantic_prompt
from core.lib import constants

EMPTY_STR = ""
SEP = " "


@dataclass
class SemanticSimConfig:
    regex = re.compile("[^a-zA-Zа-яА-Я0-9\\s]")
    EMB_SCORE_BINS = [0.89, 0.91, 0.93, 0.95]
    SUBSET_SIM_SCORE_BINS = [0.0, 0.25, 0.50, 0.75]


class SemanticSimProcessor:
    def __init__(self, model: GigaChat, emb_secret: str):
        self.model = model
        self.emb_model = GigaChatEmbeddings(
            credentials=emb_secret, verify_ssl_certs=False, scope="GIGACHAT_API_CORP"
        )
        self.config = SemanticSimConfig()

    def get_cos_sim(self, asr_response, right_answer) -> float:
        user_mes_emb = np.array(self.emb_model.embed_query(asr_response))
        trg_mes_emb = np.array(self.emb_model.embed_query(right_answer))

        cos_sim = (user_mes_emb @ trg_mes_emb) / (
            np.linalg.norm(user_mes_emb) * np.linalg.norm(trg_mes_emb)
        )

        score = np.digitize(cos_sim, self.config.EMB_SCORE_BINS, right=False) * (
            constants.MAX_TASK_SCORE / len(self.config.EMB_SCORE_BINS)
        )

        return score

    def find_citation(self, user_message: str, target_message: str):
        user_message_set = set(
            self.config.regex.sub(EMPTY_STR, user_message.strip()).lower().split(SEP)
        )
        target_message_set = set(
            self.config.regex.sub(EMPTY_STR, target_message.strip()).lower().split(SEP)
        )

        if user_message_set.issubset(target_message_set):
            score = np.digitize(
                len(user_message_set) / len(target_message_set),
                self.config.SUBSET_SIM_SCORE_BINS,
                right=False,
            ) * (constants.MAX_TASK_SCORE / len(self.config.EMB_SCORE_BINS))
            response = f"1. Смысловая схожесть: Цитирование. Оценка - {round(min(score, constants.MAX_TASK_SCORE))}%"

            return round(min(score, constants.MAX_TASK_SCORE)), response

        return None, None

    def run(self, context):
        asr_response = context.service_result.texts[0]
        right_answer = context.current_task.right_answer
        score, response = self.find_citation(asr_response, right_answer)

        if score is not None:
            return score, response, 1

        emb_score = self.get_cos_sim(asr_response, right_answer)
        sys_prompt = SystemMessage(content=semantic_prompt)

        prompt_content = HumanMessage(
            content=f"""
            {constants.TARGET_PREFIX} {right_answer}
            {constants.USER_PREFIX} {asr_response}
            "[Оценка эмбеддинговой модели]" {emb_score}
        """
        )

        prompt = [sys_prompt, prompt_content]

        response = self.model(prompt).content
        score_parser_responce = score_parser.split_parse_score(
            response, constants.SCORE_PATTERN
        )

        if not score_parser_responce[1]:
            response + "Оценка - 0%."
            score_parser_responce[1] = 1

        return (
            score_parser_responce[0],
            response,
            score_parser_responce[1],
        )
