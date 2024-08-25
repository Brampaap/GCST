from langchain.schema import SystemMessage, HumanMessage
from langchain.chat_models.gigachat import GigaChat
from langchain_community.embeddings import GigaChatEmbeddings
from modules.semantic.prompts import semantic_prompt
from modules.common.parsers import score as score_parser
import constants
from dataclasses import dataclass, field
import numpy as np


@dataclass
class SemanticSimConfig:
    max_diff: int = field(default=5)


class SemanticSimProcessor:
    def __init__(self, model: GigaChat, emb_secret: str):
        self.model = model
        self.emb_model = GigaChatEmbeddings(
            credentials=emb_secret, verify_ssl_certs=False, scope="GIGACHAT_API_PERS"
        )

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

    def run(self, user_message: str, target_message: str, client_message: str):
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
        score = score_parser.split_parse_score(response, constants.SCORE_PATTERN)

        return score, response
