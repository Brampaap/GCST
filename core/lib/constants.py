MESSAGES_PER_TASK = 3  # Client -> User -> Robot
MAX_TASK_SCORE = 100
MAX_TYPOS = 4

LF = "\n"

# Согласно стуктуре передаваемых данных
CLIENT_MSG_IND = 0
TARGET_MSG_IND = 1

USER_PREFIX = "[Сотрудник]"
TARGET_PREFIX = "[Верный ответ]"
CLIENT_PREFIX = "[Клиент]"
CHAT_PREFIX = "[Оценка ответа]"
SCORE_PATTERN = "Оценка: "
