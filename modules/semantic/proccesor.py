from langchain.schema import SystemMessage, HumanMessage
from langchain.chat_models.gigachat import GigaChat
from langchain_community.embeddings import GigaChatEmbeddings
from modules.semantic.prompts import semantic_prompt
from modules.common.parsers import score as score_parser
import constants
from dataclasses import dataclass, field
import numpy as np
import re

EMPTY_STR = ""
SEP = " "

@dataclass
class SemanticSimConfig:
    regex = re.compile("[^a-zA-Zа-яА-Я0-9\s]")


class SemanticSimProcessor:
    def __init__(self, model: GigaChat, emb_secret: str):
        self.model = model
        self.emb_model = GigaChatEmbeddings(
            credentials=emb_secret, verify_ssl_certs=False, scope="GIGACHAT_API_CORP"
        )
        self.config = SemanticSimConfig()

    def get_cos_sim(self, user_message: str, target_message: str) -> float:
        user_mes_emg = np.array(self.emb_model.embed_query(user_message))
        trg_mes_emb = np.array(self.emb_model.embed_query(target_message))
        
        cos_sim = (user_mes_emg @ trg_mes_emb) / (
            np.linalg.norm(user_mes_emg) * np.linalg.norm(trg_mes_emb)
        )
        
        score = np.digitize(cos_sim, constants.EMB_SCORE_BINS, right=False) * (
            constants.MAX_SCORE_PER_TASK / len(constants.EMB_SCORE_BINS)
        )

        return score
    
    def find_citation(self, user_message: str, target_message: str):
        user_message_set = set(self.config.regex.sub(EMPTY_STR, user_message.strip()).lower().split(SEP))
        target_message_set = set(self.config.regex.sub(EMPTY_STR, target_message.strip()).lower().split(SEP))
        
        if user_message_set.issubset(target_message_set):
            score = np.digitize(
                len(user_message_set) / len(target_message_set), 
                constants.SUBSET_SIM_SCORE_BINS, 
                right=False,
            ) * (
                constants.MAX_SCORE_PER_TASK / len(constants.EMB_SCORE_BINS)
            )
            response = f"1. Смысловая схожесть: Цитирование. Оценка: {round(min(score, constants.MAX_SCORE_PER_TASK))}%"

            return round(min(score, constants.MAX_SCORE_PER_TASK)), response

        return None, None

    def run(self, user_message: str, target_message: str):
        
        score, response = self.find_citation(user_message, target_message)

        if score is not None:
            return (score, 1), response
            
        emb_score = self.get_cos_sim(user_message, target_message)
        sys_prompt = SystemMessage(content=semantic_prompt)

        prompt_content = HumanMessage(
            content=f"""
            {constants.TARGET_PREFIX} {target_message}
            {constants.USER_PREFIX} {user_message}
            "[Оценка эмбеддинговой модели]" {emb_score}
        """
        )

        prompt = [sys_prompt, prompt_content]

        response = self.model(prompt).content
        score_parser_responce = score_parser.split_parse_score(response, constants.SCORE_PATTERN)
        
        return score_parser_responce, response
