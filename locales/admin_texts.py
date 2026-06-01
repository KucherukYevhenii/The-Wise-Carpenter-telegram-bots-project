# Усі фрази адмін-бота.
# Структура: admin_phrases["секція"]["мова"]["ключ"]
# Щоб додати нову мову — достатньо додати блок "en": {...} у кожну секцію.
# Для доступу: admin_phrases["requests"]["ua"]["new_list_empty"]

# ---------------------------------------------------------------------------
# Загальне
# ---------------------------------------------------------------------------
general = {
    "ua": {
        "back":             "Назад",
        "cancel":           "Скасувати",
        "confirm":          "Підтвердити",
        "save":             "Зберегти",
        "delete":           "Видалити",
        "edit":             "Редагувати",
        "close":            "Закрити",
        "skip":             "Пропустити",
        "next":             "▶️",
        "prev":             "◀️",
        "yes":              "Так",
        "no":               "Ні",
        "not_found":        "Нічого не знайдено.",
        "error":            "Щось пішло не так. Спробуйте ще раз.",
        "saved":            "Збережено.",
        "deleted":          "Видалено.",
        "cancelled":        "Скасовано.",
        "page":             "Сторінка",
        "of":               "з",
        "choose_action":    "Оберіть дію:",
        "ask_photo":        "Надішліть фото або натисніть «Пропустити»:",
    },
    "en": {
        "back":             "Back",
        "cancel":           "Cancel",
        "confirm":          "Confirm",
        "save":             "Save",
        "delete":           "Delete",
        "edit":             "Edit",
        "close":            "Close",
        "skip":             "Skip",
        "next":             "▶️",
        "prev":             "◀️",
        "yes":              "Yes",
        "no":               "No",
        "not_found":        "Nothing found.",
        "error":            "Something went wrong. Please try again.",
        "saved":            "Saved.",
        "deleted":          "Deleted.",
        "cancelled":        "Cancelled.",
        "page":             "Page",
        "of":               "of",
        "choose_action":    "Choose action:",
        "ask_photo":        "Send a photo or press «Skip»:",
    }
}

# ---------------------------------------------------------------------------
# Доступ / безпека
# ---------------------------------------------------------------------------
access = {
    "ua": {
        "denied":           "Доступ заборонено.",
        "superadmin_only":  "Ця дія доступна лише суперадміністратору.",
        "no_session":       "Помилка сесії. Спробуйте ще раз.",
    },
    "en": {
        "denied":           "Access denied.",
        "superadmin_only":  "This action is only available to the superadministrator.",
        "no_session":       "Session error. Please try again.",
    }
}

# ---------------------------------------------------------------------------
# /start — головне меню
# ---------------------------------------------------------------------------
menu = {
    "ua": {
        "welcome":          "Вітаємо, {name}!\n\nОберіть розділ:",
        "btn_requests":     "Заявки",
        "btn_workshops":    "Майстерні",
        "btn_support":      "Відповіді на питання",
        "btn_content":      "Контент",
        "btn_stats":        "Статистика",
        "btn_admins":       "Адміністратори",
        "btn_settings":     "Налаштування",
    },
    "en": {
        "welcome":          "Welcome, {name}!\n\nSelect a section:",
        "btn_requests":     "Requests",
        "btn_workshops":    "Workshops",
        "btn_support":      "Support",
        "btn_content":      "Content",
        "btn_stats":        "Statistics",
        "btn_admins":       "Administrators",
        "btn_settings":     "Settings",
    }
}

# ---------------------------------------------------------------------------
# /requests — заявки
# ---------------------------------------------------------------------------
requests = {
    "ua": {
        "title":                    "Заявки",
        "btn_workshop_opening":     "На відкриття майстерні",
        "btn_mobile":               "На приїзд мобільної майстерні",
        "btn_filter_new":           "Нові",
        "btn_filter_in_progress":   "В роботі",
        "btn_filter_all":           "Всі",

        "category_opening":         "Відкриття стаціонарної майстерні",
        "category_mobile":          "Приїзд мобільної майстерні",
        
        "filter_menu_title":        "<b>Категорія: {category_label}</b>\n\nОберіть статус для фільтрації списку:",
        "list_title":               "<b>{category_label}</b>\n----------------------------------------\nЗаявки · {status_label}\n\nЗнайдено: {count}",
        "list_empty":               "Заявок немає.",
        "list_item":                "{name} · {city} · {date}",
        "opening_detail": (
            "Заявка #{request_id}\n\n"
            "Ім'я: {name}\n"
            "Телефон: {phone_number}\n"
            "Країна: {country}\n"
            "Регіон: {region}\n"
            "Місто: {city}\n"
            "Церква: {church_name}\n"
            "Відомі дані: {known_information}\n"
            "Дата подачі: {created_at}\n"
            "Статус: {status}"
        ),
        "mobile_detail": (
            "Заявка #{request_id}\n\n"
            "Ім'я: {name}\n"
            "Телефон: {phone_number}\n"
            "Країна: {country}\n"
            "Регіон: {region}\n"
            "Місто: {city}\n"
            "Організація: {organization}\n"
            "Мета: {purpose}\n"
            "Дата подачі: {created_at}\n"
            "Статус: {status}"
        ),
        "detail_header":        "<b>Тип заявки: {category_label}</b>\n----------------------------------------\n",
        "btn_set_in_progress":  "Взяти в роботу",
        "btn_set_completed":    "Завершити",
        "btn_set_rejected":     "Відхилити",
        "status_changed":       "Статус заявки #{request_id} змінено на: {status}",
        
        # Шаблони сповіщень адаптовані під гарне поєднання з назвою кнопки
        "notify_in_progress":   "Вашу заявку «{req_type_label}» успішно взято в роботу.",
        "notify_completed":     "Вашу заявку «{req_type_label}» було розглянуто та завершено.",
        "notify_rejected":      "На жаль, вашу заявку «{req_type_label}» було відхилено.",
        
        "status_new":           "Нова",
        "status_in_progress":   "В роботі",
        "status_completed":     "Завершена",
        "status_rejected":      "Відхилена",
        "status_draft":         "Чернетка",
    },
    "en": {
        "title":                    "Requests",
        "btn_workshop_opening":     "For workshop opening",
        "btn_mobile":               "For mobile workshop visit",
        "btn_filter_new":           "New",
        "btn_filter_in_progress":   "In progress",
        "btn_filter_all":           "All",

        "category_opening":         "Workshop opening",
        "category_mobile":          "Mobile workshop visit",
        
        "filter_menu_title":        "<b>Category: {category_label}</b>\n\nSelect status to filter the list:",
        "list_title":               "<b>{category_label}</b>\n----------------------------------------\nRequests · {status_label}\n\nFound: {count}",
        "list_empty":               "There are no requests.",
        "list_item":                "{name} · {city} · {date}",
        "opening_detail": (
            "Request #{request_id}\n\n"
            "Name: {name}\n"
            "Phone: {phone_number}\n"
            "Country: {country}\n"
            "Region: {region}\n"
            "City: {city}\n"
            "Church: {church_name}\n"
            "Known data: {known_information}\n"
            "Submission date: {created_at}\n"
            "Status: {status}"
        ),
        "mobile_detail": (
            "Request #{request_id}\n\n"
            "Name: {name}\n"
            "Phone: {phone_number}\n"
            "Country: {country}\n"
            "Region: {region}\n"
            "City: {city}\n"
            "Organization: {organization}\n"
            "Purpose: {purpose}\n"
            "Submission date: {created_at}\n"
            "Status: {status}"
        ),
        "detail_header":         "<b>Request type: {category_label}</b>\n----------------------------------------\n",
        "btn_set_in_progress":  "Take to work",
        "btn_set_completed":    "Complete",
        "btn_set_rejected":     "Reject",
        "status_changed":       "Status of request #{request_id} changed to: {status}",
        
        "notify_in_progress":   "Your request \"{req_type_label}\" has been successfully taken to work.",
        "notify_completed":     "Your request \"{req_type_label}\" has been reviewed and completed.",
        "notify_rejected":      "Unfortunately, your request \"{req_type_label}\" has been rejected.",
        
        "status_new":           "New",
        "status_in_progress":   "In progress",
        "status_completed":     "Completed",
        "status_rejected":      "Rejected",
        "status_draft":         "Draft",
    }
}

# ---------------------------------------------------------------------------
# /workshops — майстерні
# ---------------------------------------------------------------------------
workshops = {
    "ua": {
        "title":            "Майстерні",
        "btn_list":         "Переглянути всі",
        "btn_add":          "Додати майстерню",
        "list_title":       "Майстерні · {count} шт.",
        "list_empty":       "Майстерень ще немає.",
        "list_item":        "{church_name} · {city} · {country}",
        "detail": (
            "Майстерня\n\n"
            "Країна: {country}\n"
            "Регіон: {region}\n"
            "Місто: {city}\n"
            "Церква: {church_name}\n"
            "Адреса: {address}\n"
            "Керівник: {workshop_leader}\n"
            "Телефон: {phone_number}\n"
            "Статус: {status}"
        ),
        "ask_country":      "Введіть країну:",
        "ask_region":       "Введіть регіон:",
        "ask_city":         "Введіть місто:",
        "ask_church":       "Введіть назву церкви:",
        "ask_address":      "Введіть адресу:",
        "ask_leader":       "Введіть ім'я керівника:",
        "ask_phone":        "Введіть номер телефону керівника:",
        "added":            "Майстерню успішно додано.",
        "updated":          "Майстерню оновлено.",
        "btn_deactivate":   "Деактивувати",
        "confirm_deactivate":"Ви впевнені, що хочете деактивувати цю майстерню?",
        "deactivated":      "Майстерню деактивовано.",
        "status_active":    "Активна",
        "status_closed":    "Закрита",
        
        # --- НОВІ КЛЮЧІ, ЯКІ МИ ДОДАЄМО НА ТВОЄ ПРОХАННЯ ---
        "status_draft":     "Чернетка (не опублікована)",
        "btn_activate":     "Активувати",
        "btn_clone":        "Клонувати на іншу мову",
        "ask_ws_lang":      "Оберіть мову для цієї картки майстерні:",
        "builder_title":    "Конструктор майстерні",
        "builder_desc":     "Ви можете заповнювати або редагувати поля у довільному порядку. Після завершення натисніть «Зберегти».",
        "card_language":    "Мова картки:"
    },
    "en": {
        "title":            "Workshops",
        "btn_list":         "View all",
        "btn_add":          "Add workshop",
        "list_title":       "Workshops · {count} pcs.",
        "list_empty":       "No workshops yet.",
        "list_item":        "{church_name} · {city} · {country}",
        "detail": (
            "Workshop\n\n"
            "Country: {country}\n"
            "Region: {region}\n"
            "City: {city}\n"
            "Church: {church_name}\n"
            "Address: {address}\n"
            "Leader: {workshop_leader}\n"
            "Phone: {phone_number}\n"
            "Status: {status}"
        ),
        "ask_country":      "Enter country:",
        "ask_region":       "Enter region:",
        "ask_city":         "Enter city:",
        "ask_church":       "Enter church name:",
        "ask_address":      "Enter address:",
        "ask_leader":       "Enter leader's name:",
        "ask_phone":        "Enter leader's phone number:",
        "added":            "Workshop successfully added.",
        "updated":          "Workshop updated.",
        "btn_deactivate":   "Deactivate",
        "confirm_deactivate":"Are you sure you want to deactivate this workshop?",
        "deactivated":      "Workshop deactivated.",
        "status_active":    "Active",
        "status_closed":    "Closed",
        
        # --- НОВІ КЛЮЧІ ДЛЯ EN ---
        "status_draft":     "Draft (not published)",
        "btn_activate":     "Activate",
        "btn_clone":        "Clone to another language",
        "ask_ws_lang":      "Select language for this workshop card:",
        "builder_title":    "Workshop Builder",
        "builder_desc":     "You can fill or edit fields in any order. Click 'Save' when finished.",
        "card_language":    "Language of card:"
    }
}

# ---------------------------------------------------------------------------
# /support — питання підтримки
# ---------------------------------------------------------------------------
support = {
    "ua": {
        "title":            "Питання від користувачів",
        "btn_new":          "Нові питання",
        "btn_all":          "Всі питання",
        "list_title":       "Питання · {status_label}\n\nЗнайдено: {count}",
        "list_empty":       "Питань немає.",
        "list_item":        "#{question_id} · {user_name} · {date}",
        "detail": (
            "Питання #{question_id}\n\n"
            "Від: {user_name}\n"
            "Телефон: {user_phone}\n"
            "Дата: {created_at}\n"
            "Статус: {status}\n\n"
            "{question}"
        ),
        "btn_reply":        "Відповісти",
        "ask_reply":        "Введіть відповідь для користувача:",
        "reply_sent":       "Відповідь надіслано користувачу.",
        "notify_reply":     "Відповідь на ваше питання:\n\n{text}",
        "status_new":       "Нове",
        "status_answered":  "Відповіли",
    },
    "en": {
        "title":            "User questions",
        "btn_new":          "New questions",
        "btn_all":          "All questions",
        "list_title":       "Questions · {status_label}\n\nFound: {count}",
        "list_empty":       "No questions.",
        "list_item":        "#{question_id} · {user_name} · {date}",
        "detail": (
            "Question #{question_id}\n\n"
            "From: {user_name}\n"
            "Phone: {user_phone}\n"
            "Date: {created_at}\n"
            "Status: {status}\n\n"
            "{question}"
        ),
        "btn_reply":        "Reply",
        "ask_reply":        "Enter the answer for the user:",
        "reply_sent":       "Answer sent to the user.",
        "notify_reply":     "Answer to your question:\n\n{text}",
        "status_new":       "New",
        "status_answered":  "Answered",
    }
}

# ---------------------------------------------------------------------------
# /settings — налаштування профілю адміна
# ---------------------------------------------------------------------------
settings = {
    "ua": {
        "title":            "Налаштування\n\n"
                            "Ім'я: {name}\n"
                            "Телефон: {phone_number}",
        "btn_name":         "Змінити ім'я",
        "btn_phone":        "Змінити телефон",
        "btn_language":     "Мова",
        "language_title":   "Оберіть мову:",
        "ask_name":         "Введіть нове ім'я:",
        "name_too_long":    "Ім'я не може бути довшим за 50 символів. Спробуйте ще раз.",
        "name_changed":     "Ім'я змінено на: {name}",
        "ask_phone":        "Введіть новий номер телефону:",
        "phone_changed":    "Телефон змінено на: {phone_number}",
    },
    "en": {
        "title":            "Settings\n\n"
                            "Name: {name}\n"
                            "Phone: {phone_number}",
        "btn_name":         "Change name",
        "btn_phone":        "Change phone",
        "btn_language":     "Language",
        "language_title":   "Choose language:",
        "ask_name":         "Enter new name:",
        "name_too_long":    "Name cannot be longer than 50 characters. Try again.",
        "name_changed":     "Name changed to: {name}",
        "ask_phone":        "Enter new phone number:",
        "phone_changed":    "Phone changed to: {phone_number}",
    },
}

# ---------------------------------------------------------------------------
# /content — редагування FAQ та загальної інформації
# ---------------------------------------------------------------------------
content = {
    "ua": {
        "title":            "Керування контентом бота\n\nОберіть розділ для редагування або додавання нових матеріалів:",
        "btn_faq":          "FAQ (Питання / Відповіді)",
        "btn_general_info": "Загальна інформація",
        
        # --- FAQ ---
        "faq_title":        "<b>Довідник FAQ</b>\n\nОберіть питання для перегляду або редагування:",
        "faq_list_empty":   "Список FAQ наразі порожній.",
        "btn_add_faq":      "Додати питання",
        "ask_faq_lang":     "<b>Оберіть мову</b> для нового запису FAQ:",
        "ask_faq_category": "Введіть <b>назву категорії</b> для FAQ (наприклад: <i>Оплата, Навчання</i>):",
        "ask_faq_question": "Введіть <b>текст самого питання</b>:",
        "ask_faq_answer":   "Введіть <b>розгорнуту відповідь</b> на це питання:",
        "faq_added":        "Нове питання FAQ успішно додано!",
        "faq_deleted":      "Питання FAQ успішно видалено.",
        "faq_detail": (
            "<b>Картка FAQ #{question_id}</b>\n\n"
            "<b>Мова:</b> <code>{language}</code>\n"
            "<b>Категорія:</b> <code>{category}</code>\n"
            "<b>Питання:</b> <i>{question}</i>\n\n"
            "<b>Відповідь:</b>\n{answer}"
        ),
        
        # --- Загальна інформація ---
        "info_title":       "<b>Картки загальної інформації</b>\n\nОберіть розділ контенту:",
        "info_list_empty":  "Список інформаційних карток порожній.",
        "btn_add_info":     "Додати запис",
        "ask_info_lang":    "<b>Оберіть мову</b> для картки загальної інформації:",
        "ask_info_category":"Введіть <b>назву категорії</b> інформації:",
        "ask_info_text":    "Введіть <b>основний текст</b> для цієї інформаційної картки:",
        "info_added":       "Інформаційну картку контенту успішно збережено!",
        "info_deleted":     "Інформаційну картку видалено.",
        "info_detail": (
            "<b>Інформаційна картка #{information_id}</b>\n\n"
            "<b>Мова:</b> <code>{language}</code>\n"
            "<b>Категорія:</b> <code>{category}</code>\n\n"
            "<b>Текст контенту:</b>\n{information}"
        ),
        "btn_lang_ua":      "Українська",
        "btn_lang_en":      "English",
    },
    "en": {
        "title":            "Content Management\n\nSelect a section to edit or add materials:",
        "btn_faq":          "FAQ (Questions & Answers)",
        "btn_general_info": "General Information",
        
        # --- FAQ ---
        "faq_title":        "<b>FAQ Directory</b>\n\nSelect a question to view or edit:",
        "faq_list_empty":   "FAQ list is currently empty.",
        "btn_add_faq":      "Add Question",
        "ask_faq_lang":     "<b>Select language</b> for the new FAQ record:",
        "ask_faq_category": "Enter <b>category name</b> for FAQ (e.g., <i>Payment, Training</i>):",
        "ask_faq_question": "Enter <b>the question text</b>:",
        "ask_faq_answer":   "Enter <b>detailed answer</b> for this question:",
        "faq_added":        "New FAQ question successfully added!",
        "faq_deleted":      "FAQ question deleted.",
        "faq_detail": (
            "<b>FAQ Card #{question_id}</b>\n\n"
            "<b>Language:</b> <code>{language}</code>\n"
            "<b>Category:</b> <code>{category}</code>\n"
            "<b>Question:</b> <i>{question}</i>\n\n"
            "<b>Answer:</b>\n{answer}"
        ),
        
        # --- General Information ---
        "info_title":       "<b>General Info Cards</b>\n\nSelect a content section:",
        "info_list_empty":  "General info list is empty.",
        "btn_add_info":     "Add Entry",
        "ask_info_lang":    "<b>Select language</b> for the general info card:",
        "ask_info_category":"Enter <b>category name</b> for info:",
        "ask_info_text":    "Enter <b>main text</b> for this info card:",
        "info_added":       "General info card successfully saved!",
        "info_deleted":     "Info card deleted.",
        "info_detail": (
            "<b>Info Card #{information_id}</b>\n\n"
            "<b>Language:</b> <code>{language}</code>\n"
            "<b>Category:</b> <code>{category}</code>\n\n"
            "<b>Content Text:</b>\n{information}"
        ),
        "btn_lang_ua":      "Ukrainian",
        "btn_lang_en":      "English",
    }
}

# ---------------------------------------------------------------------------
# /admins — управління адміністраторами (тільки superadmin)
# ---------------------------------------------------------------------------
admins = {
    "ua": {
        "title":                    "<b>Керування правами адміністраторів</b>\n\nТут ви можете призначати нових модераторів або знімати права з чинних:",
        "btn_list":                 "Список адмінів",
        "btn_add":                  "Призначити адміна",
        "btn_remove":               "Зняти права",
        "list_title":               "<b>Список модераторів проєкту (Всього: {count})</b>",
        "list_empty":               "Адміністраторів у базі ще немає.",
        "ask_telegram_id": (
            "<b>Призначення нового адміністратора.</b>\n\n"
            "Будь ласка, введіть цифровий <b>Telegram ID</b> користувача, якому потрібно надати права модератора. "
            "<i>Важливо: користувач повинен хоча б один раз запустити вашого клієнтського бота, щоб бути в базі даних проєкту!</i>"
        ),
        "invalid_id":               "Помилка! ID має складатися виключно з цифр. Спробуйте ще раз:",
        "user_not_found":           "Користувача з таким ID не знайдено в базі даних проєкту! Переконайтеся, що він запускав вашого користувацького бота.",
        "already_admin":            "Цей користувач вже є адміністратором проєкту.",
        "granted":                  "Користувача {name} успішно призначено адміністратором проєкту!",
        "revoked":                  "Права адміністратора для {name} успішно анульовано.",
        "cannot_remove_self":       "Ви не можете зняти права адміністратора з самого себе!",
        "cannot_remove_superadmin": "Заборонено знімати права з Головних суперадмінів системи!",
        "detail": (
            "<b>Картка адміністратора: {name}</b>\n"
            "----------------------------------------\n"
            "<b>Рівень прав:</b> {privilege}\n"
            "<b>Telegram ID:</b> <code>{telegram_id}</code>\n"
            "<b>Телефон:</b> {phone_number}\n"
            "<b>Мова інтерфейсу:</b> {language}"
        ),
        "privilege_admin":          "Модератор / Адмін",
        "privilege_superadmin":     "Суперадмін",
    },
    "en": {
        "title":                    "<b>Admin Management</b>\n\nHere you can assign new moderators or revoke permissions from current ones:",
        "btn_list":                 "Admin List",
        "btn_add":                  "Assign Admin",
        "btn_remove":               "Revoke Rights",
        "list_title":               "<b>Admin List (Total: {count})</b>",
        "list_empty":               "No administrators found in the database.",
        "ask_telegram_id": (
            "<b>Assigning a new administrator.</b>\n\n"
            "Please enter the digital <b>Telegram ID</b> of the user you want to promote. "
            "<i>Note: the user must have started your user bot at least once to exist in the database!</i>"
        ),
        "invalid_id":               "Error! ID must contain digits only. Please try again:",
        "user_not_found":           "User not found in the database. Ensure they have started the user bot.",
        "already_admin":            "This user is already an administrator.",
        "granted":                  "User {name} successfully assigned as an administrator!",
        "revoked":                  "Administrator permissions revoked from {name}.",
        "cannot_remove_self":       "You cannot revoke administrator permissions from yourself!",
        "cannot_remove_superadmin": "It is forbidden to revoke permissions from Main Superadmins!",
        "detail": (
            "<b>Admin Profile: {name}</b>\n"
            "----------------------------------------\n"
            "<b>Privilege Level:</b> {privilege}\n"
            "<b>Telegram ID:</b> <code>{telegram_id}</code>\n"
            "<b>Phone:</b> {phone_number}\n"
            "<b>Language:</b> {language}"
        ),
        "privilege_admin":          "Moderator / Admin",
        "privilege_superadmin":     "Superadmin",
    }
}

# ---------------------------------------------------------------------------
# /stats — статистика
# ---------------------------------------------------------------------------
stats = {
    "ua": {
        "title": (
            "<b>Аналітика та Статистика проєкту</b>\n\n"
            "<b>Користувачів всього:</b> <code>{total_users}</code>\n"
            "<b>Нових за 7 днів:</b> <code>{new_users_week}</code>\n\n"
            "<b>Заявки на відкриття майстерень:</b>\n"
            "  • Нових: <code>{opening_new}</code>\n"
            "  • В роботі: <code>{opening_in_progress}</code>\n"
            "  • Завершених: <code>{opening_completed}</code>\n\n"
            "<b>Заявки на приїзд мобільної:</b>\n"
            "  • Нових: <code>{mobile_new}</code>\n"
            "  • В роботі: <code>{mobile_in_progress}</code>\n"
            "  • Завершених: <code>{mobile_completed}</code>\n\n"
            "<b>Активних майстерень руху:</b> <code>{active_workshops}</code>\n"
            "<b>Нових питань:</b> <code>{support_new}</code>"
        ),
        "btn_refresh":  "Оновити дані",
    },
    "en": {
        "title": (
            "<b>Project Analytics & Statistics</b>\n\n"
            "<b>Total Users:</b> <code>{total_users}</code>\n"
            "<b>New in last 7 days:</b> <code>{new_users_week}</code>\n\n"
            "<b>Workshop Opening Requests:</b>\n"
            "  • New: <code>{opening_new}</code>\n"
            "  • In progress: <code>{opening_in_progress}</code>\n"
            "  • Completed: <code>{opening_completed}</code>\n\n"
            "<b>Mobile Workshop Requests:</b>\n"
            "  • New: <code>{mobile_new}</code>\n"
            "  • In progress: <code>{mobile_in_progress}</code>\n"
            "  • Completed: <code>{mobile_completed}</code>\n\n"
            "<b>Active Workshops:</b> <code>{active_workshops}</code>\n"
            "<b>New Questions:</b> <code>{support_new}</code>"
        ),
        "btn_refresh":  "Refresh Data",
    }
}