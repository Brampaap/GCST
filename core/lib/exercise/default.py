import base64

dialog_audio = [
    "record_1.wav",
    "record_2.wav",
]

audio_1 = base64.b64encode(open(dialog_audio[0], "rb").read()).decode("utf-8")
audio_2 = base64.b64encode(open(dialog_audio[1], "rb").read()).decode("utf-8")

sp_settings = {
    "inton_min": 9,
    "inton_max": 99,
    "temp_min": 3,
    "temp_max": 12,
    "show_friendliness": 1,
}

dialog = [
    {
        "message": "Меня уже трясет от вашего контакт-центра. Объясните, на основании какого закона ваши сотрудники сами прерывают связь?",
        "answers": [
            {
                "answer_text": "Сожалею, что произошла такая ситуация. Расскажите, что у Вас случилось?",
                "weight": 100,
            }
        ],
        "speech_params": sp_settings,
        "audio": "data:audio/mpeg;base64," + audio_1,
    },
    {
        "message": "Жалобу пишите давайте!!!",
        "answers": [
            {
                "answer_text": "Я искренне хочу Вам помочь 🙏! Расскажите, пожалуйста, с каким вопросом Вы обращались?",
                "weight": 100,
            }
        ],
        "speech_params": sp_settings,
        "audio": "data:audio/mpeg;base64," + audio_2,
    },
]
