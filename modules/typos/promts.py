import string


typo_system_prompt_template = string.Template(
    """
    Перепиши текст, исправив грамматические, орфографические и пунктуационные ошибки в тексте. 
    Текст: $typo_input_msg
    Исправленный текст:
    """
)
