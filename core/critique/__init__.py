from core.critique.common.processor import ССSProcessor
from core.critique.semantic.proccesor import SemanticSimProcessor
from core.critique.llmless.processor import TempProcessor, IntonProcessor, FriendlinessProcessor
from core.critique.typos.processor import TypoProcessor
from core.critique.eloquence.processor import EloquenceProcessor

__all__ = [
    "ССSProcessor",
    "SemanticSimProcessor",
    "TempProcessor", 
    "IntonProcessor", 
    "FriendlinessProcessor",
    "TypoProcessor",
    "EloquenceProcessor",
]
