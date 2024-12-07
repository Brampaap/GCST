import numpy as np

class IntonProcessor():
    def __init__(self, context):
        self.context = context

    def run(self, context: str):
        sr = context.service_result
        sp = context.current_task.speech_params

        if sr.inton_percentage is None:
            return 0, "1. Интонирование: Неопределено.", 0

        inton_percentage = round(sr.inton_percentage, 1)
        thresholds = [1, 2, 4, 6, 8]
        upper_bound = [max(sp.inton_min - step, 0) for step in thresholds]
        lower_bound = [sp.inton_max + step for step in thresholds]
        scores = [90, 80, 60, 40, 20, 0]
        
        inton_min_bound = max(sp.inton_min - 0.5, 0)
        inton_max_bound = sp.inton_max + 0.5

        if inton_min_bound <= inton_percentage <= inton_max_bound:
            return 100, f"1. Интонирование: всё хорошо. Оценка: 100%.", 1
        
        if inton_percentage < inton_min_bound:
            score = scores[np.digitize(inton_percentage, upper_bound, right=False)]
            return score, f"1. Интонирование: постарайтесь говорить выразительнее. Оценка: {score}%.", 1
        
        if inton_percentage > inton_min_bound:
            score = scores[np.digitize(inton_percentage, lower_bound, right=False)]
            return score, f"1. Интонирование: постарайтесь говорить выразительнее. Оценка: {score}%.", 1

class TempProcessor():
    def __init__(self, context):
        self.context = context

    def run(self, context: str):
        sr = context.service_result
        sp = context.current_task.speech_params

        if sr.temp1 is None:
            return 0, "1. Темп: Неопределено.", 0

        temp = round(sr.temp1, 1)
        thresholds = [1, 1.5, 2, 3, 4]
        faster_bound = [max(sp.temp_min - step, 0) for step in thresholds]
        slower_bound = [sp.temp_max + step for step in thresholds]
        scores = [90, 80, 60, 40, 20, 0]

        temp_min_bound = max(sp.temp_min - 0.5, 0)
        temp_max_bound = sp.temp_max + 0.5

        if temp_min_bound <= temp <= temp_max_bound:
            return 100, f"1. Темп: {temp} слог/сек. Всё хорошо. Оценка: 100%.", 1

        if temp < temp_min_bound:
            score = scores[np.digitize(temp, faster_bound, right=False)]
            return score, f"1. Темп: {temp} слог/сек. Постарайтесь говорить быстрее. Оценка: {score}%.", 1

        if temp > temp_max_bound:
            score = scores[np.digitize(temp, slower_bound, right=False)]
            return score, f"1. Темп: {temp} слог/сек. Постарайтесь говорить медленнее. Оценка: {score}%.", 1

    
class FriendlinessProcessor():
    def __init__(self, context):
        self.context = context

    def run(self, context: str):
        sr = context.service_result
        
        score = round(sr.friendliness * 100)
        n_found = 1

        response = f"1. Дружелюбие:  Оценка: {score}%."

        return score, response, n_found