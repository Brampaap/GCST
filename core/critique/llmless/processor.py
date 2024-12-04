import numpy as np

class IntonProcessor():
    def __init__(self, context):
        self.context = context

    def run(self, context: str):
        sr = context.service_result
        sp = context.current_task.speech_params

        if sr.inton_percentage is None:
            score = 0
            response = "1. Интонирование: Неопределено."
            n_found = 0
        elif sp.inton_min <= sr.inton_percentage <= sp.inton_max:
            score = 100
            response = "1. Интонирование: всё хорошо. Оценка: 100%."
            n_found = 1
        else: 
            score = 0
            response = "1. Интонирование: постарайтесь говорить выразительнее. Оценка: 0%."
            n_found = 1

        return score, response, n_found

class TempProcessor():
    def __init__(self, context):
        self.context = context

    def run(self, context: str):
        sr = context.service_result
        sp = context.current_task.speech_params

        if sr.temp1 is None:
            score = 0
            response = "1. Темп: Неопределено."
            n_found = 0
        elif sp.temp_min <= sr.temp1 <= sp.temp_max:
            score = 100
            response = f"1. Темп: всё хорошо. Оценка: 100%."
            n_found = 1
        elif sp.temp_min > sr.temp1: 
            score = 0
            response = "1. Темп: постарайтесь быстрее. Оценка: 0%."
            n_found = 1
        else: 
            score = 0
            response = "1. Темп: постарайтесь говорить медленее. Оценка: 0%."
            n_found = 1

        return score, response, n_found
    
class FriendlinessProcessor():
    def __init__(self, context):
        self.context = context
        self.classes = ["нейтрально", "зло", "позитивно", "грустно", "непонятно"]

    def run(self, context: str):
        sr = context.service_result
        
        friendliness_score = np.exp(sr.dusha[2]) / sum(np.exp(sr.dusha)) * 100
        score = round(friendliness_score)
        n_found = 1

        response = f"1. Дружелюбие:  Оценка: {score}%."

        return score, response, n_found