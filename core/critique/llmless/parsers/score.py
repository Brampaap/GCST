def split_parse_score(response: str, split_pattern: str) -> int:
    score = 0
    found = 1
    try:  # Генерация некотролируема, иногда ответ не выйдет распарсить
        splitted = response.split(split_pattern)
        if len(splitted) > 1:
            score += int("".join(list(filter(str.isdigit, splitted[-1]))))
        else:
            found = 0
    except Exception as e:
        score = 0  # FIXME: think about how to deal with such cases
        found = 0
    return score, found
