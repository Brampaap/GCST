class IntonProcessor():
    def __init__(self, context):
        self.context = context

    def run(self, context: str):
        sr = context.service_result
        sp = context.current_task.speech_params

        if sr.inton_precentage is None:
            score = 0
            response = "1. Интонирование: Неопределено."
            n_found = 0
        elif sp.inton_min <= sr.inton_precentage <= sp.inton_max:
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
        
        if sr.temp is None:
            score = 0
            response = "1. Темп: Неопределено."
            n_found = 0
        elif sp.temp_min <= sr.temp <= sp.temp_max:
            score = 100
            response = "1. Темп: всё хорошо. Оценка: 100%."
        elif sp.temp_min > sr.temp: 
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

        friendliness = sr.dusha.index(max(sr.dusha))
    
        score = 0
        response = f"1. Дружелюбие: ваша речь звучит {self.classes[friendliness]}"

        n_found = 0

        return score, response, n_found