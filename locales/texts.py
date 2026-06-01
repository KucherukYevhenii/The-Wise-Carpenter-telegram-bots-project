from enum import Enum
# фрази для реєстрації
registration_phrases = {
    "start":"Вітаємо у 'Мудрому Теслі'! \nОберіть мову / Choose your language",
    "ua":{
        "start_again": "З поверненням",
        "language_set": "Оберіть мову, будь ласка",
        "name_set": "Введіть ваше ім'я, будь ласка",
        "phone_set": "Введіть ваш номер телефону, будь ласка",
        "phone_share": "Надіслати номер",
        "registrated_successfully": "Вас зареєстровано в системі Мудрого Теслі"
    },
    "en":{
        "start_again": "Wellcome back",
        "language_set": "Please choose your language",
        "name_set": "Please enter your name",
        "phone_set": "Please enter your phone number",
        "phone_share": "Share a phone number",
        "registrated_successfully":"You are successfully registrated in the Wise Carpenter System"
    }
}

# клас з мовами
class Languages(Enum):
    UKRAINIAN = "Українська"
    ENGLISH = "English"
    UKRAINIAN_RETURN = 'ua'
    ENGLISH_RETURN = 'en'

# загальні фрази
general = {
    "ua":{
        "back": "Назад",
        "menu": "Меню",
        "next":"Вперед"
    },
    "en":{
        "back": "Back",
        "menu": "Menu",
        "next": "Next"
    }
}

# загальна інформація + найчастіше питання
general_info = {
    "ua":{
        "no_info":"Немає інформації",
        "choose_category":"Оберіть категорію",
        "select_question":"Оберіть питання у розділі",
        "page":"Сторінка",
        "faq_label": "Найчастіші питання",
        "general_info_label":"Загальна інформація"
    },
    "en":{
        "no_info":"There is no information available",
        "choose_category":"Choose the category",
        "select_question":"Select question in category",
        "page":"Page",
        "faq_label":"Frequently asked questions",
        "general_info_label":"General information"
    }
}

# --- Фрази для налаштувань ч1---
settings_phrases = {
    "ua":{
        "settings_label":"Налаштування профілю",
        "language_choose":"Оберіть мову",
        "language_changed":"Мову змінено!",
        "name_enter":"Введіть нове ім'я",
        "name_long":"Ім'я занадто довге! Спробуйте написати коротше!",
        "name_changed":"Ім'я замінено",
        "phone_share":"Натисніть кнопку нижче для поширення номеру, або введіть його вручну:",
        "phone_changed":"Номер змінено",
        "cancel_instruction":"Або відмініть і поверніться назад",
        "phone_error":"Некоректний номер телефона"
    },
    "en":{
        "settings_label":"Profile settings",
        "language_choose":"Select the language",
        "language_changed":"The language is changed",
        "name_enter":"Enter your new name",
        "name_long":"Name is too lang. Try to write it shorter!",
        "name_changed":"Name is changed",
        "phone_share":"Press the button below or type your phone manually:",
        "phone_changed":"Phone number is changed",
        "cancel_instruction":"Or cancel and come back",
        "phone_error":"Phone number is not correct"
    }
}

# --- Фрази для налаштувань ч2---
texts_settings = {
    "ua": {
        "lang": "Змінити мову",
        "name": "Змінити ім'я",
        "phone": "Змінити телефон",
        "phone_error":"Некоректний номер телефона"
    },
    "en": {
        "lang": "Change language",
        "name": "Change name",
        "phone": "Change phone",
        "phone_error":"Phone number is not correct"
    }
}

# Фрази для блоку задати питання
questions_phrases = {
    "ua":{
        "questions_label":"Задати питання",
        "questions_desc":"Ви можете задати питання, на яке може відповісти команда руху Мудрого Теслі",
        "give_question":"Задати питання",
        "archive_questions":"Архів питань",
        "empty_archive":"Ваш архів ще пустий",
        "question_desc":"Будь ласка, введіть ваше питання",
        "question_approval":"Підтвердіть ваше питання",
        "question_approve":"Підтвердити",
        "feedback": "Ваше питання успішно відправлено, очікуйте відповіді!",
        "error": "Ваше питання не відправилось, спробуйте ще раз!",
        "question_arch":"Питання",
        "status_arch":"Статус",
        "answer_arch":"Відповідь"
    },
    "en":{
        "questions_label":"Ask a question",
        "questions_desc":"You can ask a question, which can be answered by the Wise Carpenter team",
        "give_question":"Ask a question",
        "archive_questions":"Questions archive",
        "empty_archive":"Your archive is empty",
        "question_desc":"Enter your question please",
        "question_approval":"Approve your question",
        "question_approve":"Confirm",
        "feedback": "Your question is successfully sent. Please wait for response!",
        "error": "Your question is not sent! Please try again",
        "question_arch":"Question",
        "status_arch":"Status",
        "answer_arch":"Answer"
    }
}

# --- переклад статусів ---
status_phrases = {
    "ua":{
        "status_new":"Новий",
        "status_in_progress":"В процесі",
        "status_completed":"Готово",
        "status_rejected":"Відмовлено",
        "status_closed":"Закрито"
    },
    "en":{
        "status_new":"New",
        "status_in_progress":"In progress",
        "status_completed":"Completed",
        "status_rejected":"Rejected",
        "status_closed":"Closed"
    }
}

# --- Фрази для майстерень ---
workshop_phrases = {
    "ua": {
        "label":"майстерні руху Мудрий Тесля",
        "title": "Наші майстерні",
        "choose_country": "Оберіть країну:",
        "choose_region": "Оберіть регіон:",
        "choose_city": "Оберіть місто:",
        "choose_workshop": "Оберіть майстерню:",
        "back_to": "Назад до",
        "country_lvl": "країн",
        "region_lvl": "регіонів",
        "city_lvl": "міст",
        "list_lvl": "списку",
        "leader": "Лідер",
        "address": "Адреса",
        "phone": "Телефон"
    },
    "en": {
        "label":"The Wise Carpenter's workshops",
        "title": "Our Workshops",
        "choose_country": "Choose a country:",
        "choose_region": "Choose a region:",
        "choose_city": "Choose a city:",
        "choose_workshop": "Choose a workshop:",
        "back_to": "Back to",
        "country_lvl": "countries",
        "region_lvl": "regions",
        "city_lvl": "cities",
        "list_lvl": "list",
        "leader": "Leader",
        "address": "Address",
        "phone": "Phone"
    }
}


# --- Фрази для анкети на запуск майстерні ---
start_workshop_phrases = {
    "ua":{
        "title":"Анкета для запуску майстерні",
        "desc":"Тут можна заповнити анкету на запуск майстерні у вашій помісній Церкві. Нам необіхдно знати деяку інформацію: локація вашої Церкви та інформацію, що ви вже знаєте про запуск майстерні.",
        "new_form":"Нова анкета",
        "continue_form":"Продовжити заповнення анкети",
        "form_archive":"Архів анкет",
        "country_name":"Країна",
        "region_name":"Регіон",
        "city_name":"Місто",
        "church_name":"Назва Церкви",
        "info":"Інформація",
        "back_to_form":"Назад до анкети",
        "set_country":"Написати країну",
        "set_region":"Написати регіон",
        "set_city":"Написати місто",
        "set_church":"Написати назву Церкви",
        "set_info":"Написати інформацію",
        "send_form":"Відправити анкету",
        "cancel_form":"Відмінити анкету",
        "confirm_canceling":"Підтвердити відміну",
        "confirm_canceling_desc":"Підтвердіть, будь ласка, відміну",
        "form_sent":"Анкета відправлена",
        "form_archive":"Архів анкет",
        "no_archived":"Немає архівованих анкет",
        "archive_desc":"Тут зібрані заархівовані анкети",
        "status":"Статус",
        "date":"Дата",
        "back_to_archive":"Назад до архіву"
    },
    "en":{
        "title":"Form to start a workshop",
        "desc":"You can fill the form to start the workshop in your local church here. We need to know information about location of your church and the information you've already known about starting the workshop",
        "new_form":"New form",
        "continue_form":"Continue filling the form",
        "form_archive":"Achive of forms",
        "country_name":"Country",
        "region_name":"Region",
        "city_name":"City",
        "church_name":"The name of the church",
        "info":"Information",
        "back_to_form":"Back to form",
        "set_country":"Set the country",
        "set_region":"Set the region",
        "set_city":"Set the city",
        "set_church":"Set the church's name",
        "set_info":"Set the information",
        "send_form":"Send the form",
        "cancel_form":"Cancel the form",
        "confirm_canceling":"Confirm the canceling",
        "confirm_canceling_desc":"Confirm the canceling please",
        "form_sent":"The form is sent",
        "form_archive":"The archive of forms",
        "no_archived":"There is no archived forms",
        "archive_desc":"There are the archived forms",
        "status":"Status",
        "date":"Date",
        "back_to_archive":"Back to the archive"
    }
}


# --- Фрази для анкети на запит мобільної майстерні майстерні ---
mobile_workshop_phrases = {
    "ua": {
        "title": "Анкета на запит мобільної майстерні",
        "desc": "Тут можна заповнити анкету на приїзд мобільної майстерні до вас. Нам необхідно знати вашу локацію та мету приїзду.",
        "new_form": "Нова анкету",
        "continue_form": "Продовжити заповнення",
        "form_archive": "Архів анкет",
        "no_archived": "Немає архівованих анкет",
        "archive_desc": "Тут зібрані заархівовані анкети",
        "country_name": "Країна",
        "region_name": "Регіон",
        "city_name": "Місто",
        "organization_name": "Організація",
        "purpose_name": "Мета приїзду",
        "set_country": "Вкажіть країну",
        "set_region": "Вкажіть регіон",
        "set_city": "Вкажіть місто",
        "set_organization": "Напишіть назву організації",
        "set_purpose": "Опишіть мету приїзду",
        "send_form": "Відправити анкету",
        "cancel_form": "Відмінити анкету",
        "confirm_canceling": "Підтвердити відміну",
        "confirm_canceling_desc": "Підтвердіть, будь ласка, відміну",
        "back_to_form": "Назад до анкети",
        "back_to_archive": "Назад до архіву",
        "status": "Статус",
        "date": "Дата",
        "form_sent": "Анкета відправлена"
    },
    "en": {
        "title": "Mobile workshop form",
        "desc": "Here you can fill the form to request a mobile workshop visit. We need to know your location and the purpose of the visit.",
        "new_form": "New from",
        "continue_form": "Continue filling the form",
        "form_archive": "Archive of forms",
        "no_archived": "There is no archived forms",
        "archive_desc": "Here are the archived forms",
        "country_name": "Country",
        "region_name": "Region",
        "city_name": "City",
        "organization_name": "Organization",
        "purpose_name": "Purpose",
        "set_country": "Set the country",
        "set_region": "Set the region",
        "set_city": "Set the city",
        "set_organization": "Set the organization name",
        "set_purpose": "Set the purpose of coming",
        "send_form": "Send the form",
        "cancel_form": "Cancel form",
        "confirm_canceling": "Confirm the canceling",
        "confirm_canceling_desc": "Confirm the canceling please",
        "back_to_form": "Back to form",
        "back_to_archive": "Back to archive",
        "status": "Status",
        "date": "Date",
        "form_sent": "The form is sent"
    }
}