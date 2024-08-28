def split_parse_score(response: str, split_pattern: str) -> int:
    score = 0
    found = 1
    try:  # Sometimes the response format may be incorrect
        score += int(
            "".join(list(filter(str.isdigit, response.split(split_pattern)[-1])))
        )
    except Exception as e:
        score = 0  # FIXME: think about how to deal with such cases
        found = 0
    return score, found
