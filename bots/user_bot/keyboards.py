from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales.texts import registration_phrases as reg, Languages as lang, general as gen, texts_settings as sett, questions_phrases as qst, status_phrases as sts, start_workshop_phrases as sw_phrases, mobile_workshop_phrases

from database.models import Status

lang_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text= lang.UKRAINIAN.value, callback_data=lang.UKRAINIAN_RETURN.value),
        InlineKeyboardButton(text = lang.ENGLISH.value, callback_data=lang.ENGLISH_RETURN.value)
    ]
])

# --- Кнопка для запиту телефону ---

def get_phone_number_kb_reg(user_lang:str):
    if user_lang not in reg:
        user_lang = lang.ENGLISH_RETURN.value
        
    text = reg[user_lang].get('phone_share')
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text = text ,request_contact=True)]
    ],resize_keyboard=True, one_time_keyboard=True)


# --- Утворення сітки кнопок для категорій загальної інформації
def get_info_categories_kb(categories_list, user_lang: str,  page: int = 0, limit: int = 5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Вираховуємо зріз для поточної сторінки
    start_offset = page * limit
    end_offset = start_offset + limit
    current_page_items = categories_list[start_offset:end_offset]
    
    # Додаємо кнопки категорій
    for item in current_page_items:
        builder.button(
            text=item.category, 
            callback_data=f"info_id:{item.information_id}"
        )
    
    builder.adjust(1) # Кожна категорія з нового рядка
    
    # Додаємо навігаційні кнопки
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text=gen[user_lang].get('back'), callback_data=f"info_page:{page - 1}"))
    
    if end_offset < len(categories_list):
        nav_buttons.append(InlineKeyboardButton(text=gen[user_lang].get('next'), callback_data=f"info_page:{page + 1}"))
    
    if nav_buttons:
        builder.row(*nav_buttons)
        
    return builder.as_markup()

# --- Створення кнопки назад ---
def get_back_kb(lang:str, callback_data:str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{gen[lang].get('back')}", callback_data=callback_data)]
    ])


# --- Створення сітки категорій для FAQ ---
def get_faq_categories_kb(categories, user_lang: str, page: int = 0, limit: int = 5):
    """Клавіатура для вибору категорії FAQ"""
    builder = InlineKeyboardBuilder()
    
    start_offset = page * limit
    end_offset = start_offset + limit
    current_items = categories[start_offset:end_offset]
    
    for cat in current_items:
        # Передаємо назву категорії в callback
        builder.button(text=cat, callback_data=f"faq_cat:{cat}")
    
    builder.adjust(1)
    
    # Навігація
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text=gen[user_lang].get("back"), callback_data=f"faq_cat_page:{page-1}"))
    if end_offset < len(categories):
        nav_buttons.append(InlineKeyboardButton(text=gen[user_lang].get("next"), callback_data=f"faq_cat_page:{page+1}"))
    
    if nav_buttons:
        builder.row(*nav_buttons)
    return builder.as_markup()

# --- Створення сітки для питань в категорії FAQ ---
def get_faq_questions_kb(questions, user_lang: str, category: str, page: int = 0, limit: int = 5):
    """Клавіатура для вибору конкретного запитання у категорії"""
    builder = InlineKeyboardBuilder()
    
    start_offset = page * limit
    end_offset = start_offset + limit
    current_items = questions[start_offset:end_offset]
    
    for q in current_items:
        builder.button(text=q.question, callback_data=f"faq_id:{q.question_id}")
    
    builder.adjust(1)
    
    # Навігація + кнопка "Назад до категорій"
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text=gen[user_lang].get("back"), callback_data=f"faq_q_page:{category}:{page-1}"))
    
    nav_row.append(InlineKeyboardButton(text=f"{gen[user_lang].get('menu')} FAQ", callback_data="faq_main")) # Повернення до списку категорій
    
    if end_offset < len(questions):
        nav_row.append(InlineKeyboardButton(text=gen[user_lang].get("next"), callback_data=f"faq_q_page:{category}:{page+1}"))
    
    builder.row(*nav_row)
    return builder.as_markup()


def get_settings_kb(user_lang: str) -> InlineKeyboardMarkup:
    """Клавіатура головного меню налаштувань"""
    builder = InlineKeyboardBuilder()
    
    # Перевірка на випадок, якщо мова не підтримується
    L = sett[user_lang]

    back_text = gen[user_lang].get('back')
    
    # Додаємо кнопки
    builder.button(text=L["lang"], callback_data="set_lang_menu")
    builder.button(text=L["name"], callback_data="set_name_start")
    builder.button(text=L["phone"], callback_data="set_phone_start")

    # builder.button(text=back_text, callback_data="main_menu")
    
    # Розміщуємо по одній кнопці в ряд для зручності натискання
    builder.adjust(1)
    
    return builder.as_markup()

def get_lang_settings_kb(user_lang: str) -> InlineKeyboardMarkup:
    """Вибір мови з кнопкою повернення до налаштувань"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text=lang.UKRAINIAN.value, callback_data=f"set_lang:{lang.UKRAINIAN_RETURN.value}")
    builder.button(text=lang.ENGLISH.value, callback_data=f"set_lang:{lang.ENGLISH_RETURN.value}")
    
    # Кнопка "Назад" до меню налаштувань
    builder.button(text=gen[user_lang].get('back'), callback_data="settings_back")
    
    builder.adjust(2, 1) # Дві кнопки мови в ряд, кнопка "Назад" — під ними
    return builder.as_markup()

def get_name_change_kb(user_lang: str):
    builder = InlineKeyboardBuilder()
    builder.button(text=gen[user_lang].get('back'), callback_data="settings_back")
    return builder.as_markup()

# --- Оновлена кнопка для запиту телефону (додаємо кнопку скасування) ---
def get_phone_number_kb(user_lang: str):
    if user_lang not in reg:
        user_lang = lang.ENGLISH_RETURN.value
        
    text = reg[user_lang].get('phone_share')
    back_text = gen[user_lang].get('back')
    
    # Використовуємо Inline кнопку під повідомленням для скасування, 
    # бо в ReplyKeyboardMarkup кнопка "Назад" просто надішле текст.
    builder = InlineKeyboardBuilder()
    builder.button(text=back_text, callback_data="settings_back")
    
    # Повертаємо і Reply (для контакту) і Inline (для скасування)
    reply_kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=text, request_contact=True)]
    ], resize_keyboard=True, one_time_keyboard=True)
    
    return reply_kb, builder.as_markup()


# --- Кнопки функції задання питань ---
def get_qstort_main_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    L = qst[lang]
    
    # Кнопка "Задати питання"
    builder.button(text=f"{L['give_question']}", callback_data="ask_qstort_start")
    
    # Кнопка "Архів питань"
    builder.button(text=f"{L['archive_questions']}", callback_data="qstort_archive")
    
    # Кнопка повернення до головного меню бота
    # builder.button(text=f {gen[lang].get('menu', 'Menu')}", callback_data="main_menu")
    
    builder.adjust(1) # Кнопки одна під одною
    return builder.as_markup()


# --- 2. Кнопка підтвердження перед відправкою ---
def get_confirm_question_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    L = qst[lang]
    
    # Підтвердити
    builder.button(text=f"{L['question_approve']}", callback_data="confirm_question_send")
    
    # Змінити (повертає до введення тексту)
    builder.button(text=f"{gen[lang].get('back')}", callback_data="ask_qstort_start")
    
    builder.adjust(1)
    return builder.as_markup()


# --- 3. Кнопка скасування (під час введення) ---
def get_qstort_cancel_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Використовуємо універсальну кнопку "Назад"
    builder.button(text=f"{gen[lang].get('back')}", callback_data="open_qstort")
    return builder.as_markup()


# --- 4. Архів питань з пагінацією ---
def get_archive_kb(questions, lang: str, page: int = 0, limit: int = 5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Розрахунок елементів для поточної сторінки
    start_offset = page * limit
    end_offset = start_offset + limit
    current_page_items = questions[start_offset:end_offset]
    
    for q in current_page_items:
        # Безпечно мапимо статус через нижній регістр для пошуку ключа локалізації
        status_str = q.status.value.lower() if hasattr(q.status, 'value') else str(q.status).lower()
        status_key = f"status_{status_str}"
        status = sts[lang].get(status_key, status_str)
            
        # Обрізаємо текст питання для кнопки (прев'ю)
        preview = (q.question[:20] + "..") if len(q.question) > 20 else q.question
        
        # Колбек містить ID питання та поточну сторінку для повернення
        builder.button(
            text=f"{status}: {preview}", 
            callback_data=f"view_q:{q.question_id}:{page}"
        )
    
    builder.adjust(1)
    
    # Навігаційна панель (Стрілки)
    nav_buttons = []
    
    # Стрілка вліво
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text=gen[lang].get("back"), callback_data=f"archive_page:{page - 1}"))
    
    # Центральна кнопка виходу до меню підтримки
    nav_buttons.append(InlineKeyboardButton(text=gen[lang].get('menu'), callback_data="open_qstort"))
    
    # Стрілка вправо
    if end_offset < len(questions):
        nav_buttons.append(InlineKeyboardButton(text=gen[lang].get('next'), callback_data=f"archive_page:{page + 1}"))
    
    builder.row(*nav_buttons)
    return builder.as_markup()


# --- Кнопка навігації в майстернях
def get_workshop_nav_kb(lang, items, current_prefix, next_prefix,  back_steps, page=0, limit=5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # 1. Кнопки вибору (Країни/Регіони/Міста/Майстерні)
    start, end = page * limit, (page + 1) * limit
    for item in items[start:end]:
        if hasattr(item, 'workshop_id'): # Якщо це об'єкт Workshop
            builder.button(text=f"{item.church_name}", callback_data=f"ws_view:{item.workshop_id}")
        else: # Якщо це рядок (Країна/Регіон/Місто)
            builder.button(text=str(item), callback_data=f"{next_prefix}:{item}:0")
    
    builder.adjust(1)

    # 2. Пагінація
    nav = []
    if page > 0:
        # Для Назад робимо page - 1
        nav.append(InlineKeyboardButton(text=gen[lang].get("back"), callback_data=f"{current_prefix}:{page-1}"))
    if end < len(items):
        # Для Вперед робимо page + 1
        nav.append(InlineKeyboardButton(text=gen[lang].get("next"), callback_data=f"{current_prefix}:{page+1}"))
    if nav: 
        builder.row(*nav)

    # 3. Кнопки швидкого повернення (Твоя ідея)
    if back_steps:
        for label, call in back_steps:
            builder.row(InlineKeyboardButton(text=f"{label}", callback_data=call))
        
    return builder.as_markup()


# --- кнопка меню анкети на вікриття майстерні ---
def get_q_main_kb(lang, has_draft: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    p = sw_phrases[lang]

    if not has_draft:
        builder.button(text=f"{p['new_form']}", callback_data="q_new")
    if has_draft:
        builder.button(text=f"{p['continue_form']}", callback_data="q_continue")
    builder.button(text=f"{p['form_archive']}", callback_data="q_archive")
    # builder.button(text=f"{gen[lang]['back']}", callback_data="main_menu")
    
    builder.adjust(1)
    return builder.as_markup()

# --- система заповнення анкети ---
def get_q_form_kb(lang, data) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    p = sw_phrases[lang]
    
    # Визначаємо статус заповнення (✅/❌)
    c_check = "✅" if data.get('country') else "❌"
    r_check = "✅" if data.get('region') else "❌"
    city_check = "✅" if data.get('city') else "❌"
    ch_check = "✅" if data.get('church_name') else "❌"
    i_check = "✅" if data.get('known_information') else "❌"

    buttons = [
        InlineKeyboardButton(text=f"{c_check} {p['set_country']}", callback_data="q_edit_country"),
        InlineKeyboardButton(text=f"{r_check} {p['set_region']}", callback_data="q_edit_region"),
        InlineKeyboardButton(text=f"{city_check} {p['set_city']}", callback_data="q_edit_city"),
        InlineKeyboardButton(text=f"{ch_check} {p['set_church']}", callback_data="q_edit_church"),
        InlineKeyboardButton(text=f"{i_check} {p['set_info']}", callback_data="q_edit_info")
    ]

    for button in buttons:
        builder.row(button)
    
    # Кнопка відправки (якщо заповнені ключові поля)
    if all([data.get('city'), data.get('church_name'), data.get('known_information'), data.get('country'), data.get('region')]):
        builder.row(InlineKeyboardButton(text=f"{p['send_form']}", callback_data="q_send"))
    
    builder.row(InlineKeyboardButton(text=f"{p['cancel_form']}", callback_data="q_cancel"))
    builder.row(InlineKeyboardButton(text=f"{gen[lang]['back']}", callback_data="questionnaire_menu"))
    
    return builder.as_markup()


# --- Архів анкет на заповнення  ---
def get_q_archive_kb(lang, requests) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    S = sts[lang]
    
    for req_item in requests:
        # Безпечно витягуємо рядок статусу у нижньому регістрі для пошуку перекладу
        status_str = req_item.status.value.lower() if hasattr(req_item.status, 'value') else str(req_item.status).lower()
        status_label = S.get(f"status_{status_str}", status_str)
        
        btn_text = f"{status_label}: {req_item.church_name} ({req_item.city})"
        builder.button(text=btn_text, callback_data=f"q_arch_view:{req_item.request_id}")
    
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text=f"{sw_phrases[lang]['back_to_form']}", callback_data="questionnaire_menu"))
    return builder.as_markup()

# --- кнопка меню анкети на запит мобільної майстерні ---
def get_mq_main_kb(lang, has_draft: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    p = mobile_workshop_phrases[lang]
    
    if not has_draft:
        builder.button(text=p['new_form'], callback_data="mq_new")
    else:
        builder.button(text=p['continue_form'], callback_data="mq_continue")
    builder.button(text=p['form_archive'], callback_data="mq_archive")
    builder.adjust(1)
    return builder.as_markup()

# --- sistema заповнення анкети ---
def get_mq_form_kb(lang, data) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    p = mobile_workshop_phrases[lang]
    
    # Статуси
    c_check = "✅" if data.get('country') else "❌"
    r_check = "✅" if data.get('region') else "❌"
    city_check = "✅" if data.get('city') else "❌"
    org_check = "✅" if data.get('organization') else "❌" # Нове
    p_check = "✅" if data.get('purpose') else "❌"

    builder.row(InlineKeyboardButton(text=f"{c_check} {p['set_country']}", callback_data="mq_edit:country"))
    builder.row(InlineKeyboardButton(text=f"{r_check} {p['set_region']}", callback_data="mq_edit:region"))
    builder.row(InlineKeyboardButton(text=f"{city_check} {p['set_city']}", callback_data="mq_edit:city"))
    builder.row(InlineKeyboardButton(text=f"{org_check} {p['set_organization']}", callback_data="mq_edit:organization")) # Нова кнопка
    builder.row(InlineKeyboardButton(text=f"{p_check} {p['set_purpose']}", callback_data="mq_edit:purpose"))
    
    # Кнопка відправки (тепер перевіряємо і організацію)
    if all([data.get('country'), data.get('region'), data.get('city'), data.get('organization'), data.get('purpose')]):
        builder.row(InlineKeyboardButton(text=f"{p['send_form']}", callback_data="mq_send"))
    
    builder.row(
        InlineKeyboardButton(text=f"{p['cancel_form']}", callback_data="mq_cancel"),
        InlineKeyboardButton(text=f"{p['back_to_form']}", callback_data="mobile_menu")
    )
    return builder.as_markup()

# --- Архів анкет на заповнення  ---
def get_mq_archive_kb(lang, requests) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    S = sts[lang] 
    
    for req_item in requests:
        # Безпечно витягуємо рядок статусу у нижньому регістрі для пошуку перекладу
        status_str = req_item.status.value.lower() if hasattr(req_item.status, 'value') else str(req_item.status).lower()
        status_label = S.get(f"status_{status_str}", status_str)
        
        # Для мобільної анкети виводимо Організацію та Місто
        # Якщо раптом організація пуста, виводимо лише місто
        org_info = req_item.organization if req_item.organization else "—"
        btn_text = f"{status_label}: {org_info} ({req_item.city})"
        
        builder.button(
            text=btn_text, 
            callback_data=f"mq_arch_view:{req_item.request_id}" # Спеціальний префікс для мобілок
        )
    
    builder.adjust(1)
    
    # Кнопка повернення веде саме до головного меню МОБІЛЬНОЇ майстерні
    builder.row(InlineKeyboardButton(
        text=f"{mobile_workshop_phrases[lang]['back_to_form']}", 
        callback_data="mobile_menu"
    ))
    
    return builder.as_markup()