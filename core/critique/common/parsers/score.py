def split_parse_score(response: str, split_pattern: str) -> int:
    score = 0
    found = 0
    try:  # Генерация некотролируема, иногда ответ не выйдет распарсить
        splitted = response.split(split_pattern)
        if len(splitted) > 1:
            score += int("".join(list(filter(str.isdigit, splitted[-1]))))
            found = 1
        return score, found
    except Exception as e:
        return score, found
    
    
