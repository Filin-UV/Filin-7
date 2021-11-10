
langs = ["Русский", "English", "Deutsch"]

russian = ["Филин-7","Настройки","Режим:","Смешанный","УФ-канал","Видимый","Усиление",
           "Фото","Запись","Темп","Влажн","Язык","Русский","Час.пояс","Назад","Носитель","Отсут.","Формат.","Обновить\n ПО",""]
english = ["Filin-7","Settings","Mode:","Mixed","UV","Visual","Gain",
           "Photo","Record","Temp","Humid","Language","English","Time zone","Return","Memory","Not found","Format","Update\n software"]
deutsch = ["Filin-7","Einstellung","Arbeitsweise","Gemischt","UV","Sichtbar","Amplifikation",
           "Photo","Aufnehmen","Temp","Feuchte","Sprache","Deutsch","Zeitzone","Zurück","Speicher","Fehlen","Format.","Software \n aktualis."]

def change_lang(lang):
    lang_dict = []
    if lang == 0:
        lang_dict = russian
    elif lang == 1:
        lang_dict = english
    elif lang == 2:
        lang_dict = deutsch
    return lang_dict
