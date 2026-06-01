from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import AdminPrivilege

from locales.admin_texts import general as gen, menu as mn, requests as req, \
    workshops as ws, support as sup, content as cnt, stats as sts, admins as adm, settings as sett

from database.models import Status


# ---------------------------------------------------------------------------
# Загальні / повторювані
# ---------------------------------------------------------------------------
def back_kb(lang: str, callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=gen[lang].get("back", "Назад"), callback_data=callback_data)
    ]])

def confirm_kb(lang: str, confirm_cb: str, cancel_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=gen[lang].get("confirm"), callback_data=confirm_cb),
        InlineKeyboardButton(text=gen[lang].get("cancel"),  callback_data=cancel_cb),
    ]])

def yes_no_kb(lang: str, yes_cb: str, no_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=gen[lang].get("yes"), callback_data=yes_cb),
        InlineKeyboardButton(text=gen[lang].get("no"),  callback_data=no_cb),
    ]])

def skip_photo_kb(lang: str, skip_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=gen[lang].get("skip"), callback_data=skip_cb)
    ]])

def lang_select_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=cnt[lang].get("btn_lang_ua", "UA"), callback_data="lang:ua"),
            InlineKeyboardButton(text=cnt[lang].get("btn_lang_en", "EN"), callback_data="lang:en"),
        ],
        # Додаємо кнопку повернення до головного меню контенту
        [InlineKeyboardButton(text=gen[lang].get("back", "Назад"), callback_data="menu:content")]
    ])

def _pagination_row(lang: str, page: int, total: int, cb_prefix: str) -> list:
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(
            text=gen[lang].get("prev", "«"), callback_data=f"{cb_prefix}:{page - 1}"
        ))
    if (page + 1) < total:
        buttons.append(InlineKeyboardButton(
            text=gen[lang].get("next", "»"), callback_data=f"{cb_prefix}:{page + 1}"
        ))
    return buttons


# ---------------------------------------------------------------------------
# Головне меню
# ---------------------------------------------------------------------------
def main_menu_kb(lang: str, is_superadmin: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=mn[lang].get("btn_requests"),  callback_data="menu:requests")
    builder.button(text=mn[lang].get("btn_workshops"), callback_data="menu:workshops")
    builder.button(text=mn[lang].get("btn_support"),   callback_data="menu:support")
    builder.button(text=mn[lang].get("btn_content"),   callback_data="menu:content")
    builder.button(text=mn[lang].get("btn_stats"),     callback_data="menu:stats")
    if is_superadmin:
        builder.button(text=mn[lang].get("btn_admins"), callback_data="menu:admins")
    builder.button(text=mn[lang].get("btn_settings"),  callback_data="menu:settings")
    builder.adjust(2)
    return builder.as_markup()


# ---------------------------------------------------------------------------
# Заявки
# ---------------------------------------------------------------------------
def requests_menu_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=req[lang].get("btn_workshop_opening"), callback_data="req_type:opening")],
        [InlineKeyboardButton(text=req[lang].get("btn_mobile"),           callback_data="req_type:mobile")],
        [InlineKeyboardButton(text=gen[lang].get("back"),                 callback_data="menu:main")],
    ])

def requests_filter_kb(lang: str, req_type: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=req[lang].get("btn_filter_new"),         callback_data=f"req_filter:{req_type}:NEW"),
            InlineKeyboardButton(text=req[lang].get("btn_filter_in_progress"), callback_data=f"req_filter:{req_type}:IN_PROGRESS"),
            InlineKeyboardButton(text=req[lang].get("btn_filter_all"),         callback_data=f"req_filter:{req_type}:ALL"),
        ],
        [InlineKeyboardButton(text=gen[lang].get("back"), callback_data="menu:requests")],
    ])

def requests_list_kb(lang: str, items: list, req_type: str, status_filter: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        user_name = item.user.name if item.user else "Anonymous"
        label = f"{user_name} · {item.city}"
        builder.button(text=label, callback_data=f"req_detail:{req_type}:{item.request_id}")
    builder.adjust(1)

    nav = _pagination_row(lang, page, total_pages, f"req_page:{req_type}:{status_filter}")
    if nav:
        builder.row(*nav)

    builder.row(InlineKeyboardButton(text=gen[lang].get("back"), callback_data=f"req_type:{req_type}"))
    return builder.as_markup()

def request_detail_kb(lang: str, req_type: str, request_id: int, current_status: str, status_filter: str = "ALL") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if current_status == Status.NEW.value:
        builder.button(text=req[lang].get("btn_set_in_progress"), callback_data=f"req_status:{req_type}:{request_id}:IN_PROGRESS")
        builder.button(text=req[lang].get("btn_set_rejected"),    callback_data=f"req_status:{req_type}:{request_id}:REJECTED")
    elif current_status == Status.IN_PROGRESS.value:
        builder.button(text=req[lang].get("btn_set_completed"),   callback_data=f"req_status:{req_type}:{request_id}:COMPLETED")
        builder.button(text=req[lang].get("btn_set_rejected"),    callback_data=f"req_status:{req_type}:{request_id}:REJECTED")
    elif current_status in [Status.COMPLETED.value, Status.REJECTED.value]:
        restore_text = "Повернути на розгляд" if lang == "ua" else "Restore request"
        builder.button(text=restore_text, callback_data=f"req_status:{req_type}:{request_id}:IN_PROGRESS")

    builder.adjust(2)
    builder.row(InlineKeyboardButton(text=gen[lang].get("back"), callback_data=f"req_filter:{req_type}:{status_filter}"))
    return builder.as_markup()


# ---------------------------------------------------------------------------
# Майстерні
# ---------------------------------------------------------------------------
def workshops_menu_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=cnt[lang].get("btn_lang_ua", "UA"), callback_data="ws:filter:ua"),
            InlineKeyboardButton(text=cnt[lang].get("btn_lang_en", "EN"), callback_data="ws:filter:en"),
            InlineKeyboardButton(text=req[lang].get("btn_filter_all", "ALL"), callback_data="ws:filter:all")
        ],
        [InlineKeyboardButton(text=ws[lang].get("btn_add"),  callback_data="ws:add")],
        [InlineKeyboardButton(text=gen[lang].get("back"),    callback_data="menu:main")],
    ])

def workshops_list_kb(lang: str, items: list, lang_filter: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        label = f"[{item.language.upper()}] {item.church_name} · {item.city}"
        builder.button(text=label, callback_data=f"ws_detail:{item.workshop_id}:{lang_filter}")
    builder.adjust(1)

    nav = _pagination_row(lang, page, total_pages, f"ws_page:{lang_filter}")
    if nav:
        builder.row(*nav)

    builder.row(InlineKeyboardButton(text=gen[lang].get("back"), callback_data="menu:workshops"))
    return builder.as_markup()

def workshop_detail_kb(lang: str, workshop_id: int, status: str, lang_filter: str = "all") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.button(text=gen[lang].get("edit"), callback_data=f"ws_edit_card:{workshop_id}:{lang_filter}")
    
    if status == Status.ACTIVE.value:
        builder.button(text=ws[lang].get("btn_deactivate"), callback_data=f"ws_status:{workshop_id}:CLOSED:{lang_filter}")
    else:
        builder.button(text=ws[lang].get("btn_activate"), callback_data=f"ws_status:{workshop_id}:ACTIVE:{lang_filter}")
        
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text=gen[lang].get("delete"), callback_data=f"ws_delete_item:{workshop_id}:{lang_filter}"),
    )
    builder.row(
        InlineKeyboardButton(text=ws[lang].get("btn_clone"), callback_data=f"ws_clone:{workshop_id}:{lang_filter}")
    )
    builder.row(InlineKeyboardButton(text=gen[lang].get("back"), callback_data=f"ws:list:{lang_filter}:0"))
    return builder.as_markup()

def workshop_edit_fields_kb(lang: str, workshop_id: int, lang_filter: str = "all") -> InlineKeyboardMarkup:
    fields = {
        "ua": [
            ("Країна", "country"), ("Регіон", "region"), ("Місто", "city"),
            ("Церква", "church_name"), ("Адреса", "address"), ("Керівник", "workshop_leader"),
            ("Телефон", "phone_number"), 
            # ("Фото", "photo")
        ],
        "en": [
            ("Country", "country"), ("Region", "region"), ("City", "city"),
            ("Church", "church_name"), ("Address", "address"), ("Leader", "workshop_leader"),
            ("Phone", "phone_number"), 
            # ("Photo", "photo")
        ]
    }
    builder = InlineKeyboardBuilder()
    for label, field in fields.get(lang, fields["ua"]):
        builder.button(text=label, callback_data=f"ws_field:{workshop_id}:{field}:{lang_filter}")
    builder.adjust(2)
    
    builder.row(
        InlineKeyboardButton(text=cnt[lang].get("btn_lang_ua", "UA"), callback_data=f"ws_set_lang_value:{workshop_id}:ua:{lang_filter}"),
        InlineKeyboardButton(text=cnt[lang].get("btn_lang_en", "EN"), callback_data=f"ws_set_lang_value:{workshop_id}:en:{lang_filter}")
    )
    
    builder.row(
        InlineKeyboardButton(text=gen[lang].get("save"), callback_data=f"ws_save_card:{workshop_id}:{lang_filter}"),
        InlineKeyboardButton(text=gen[lang].get("cancel"), callback_data=f"ws_cancel_draft:{workshop_id}:{lang_filter}")
    )
    return builder.as_markup()


# ---------------------------------------------------------------------------
# Підтримка
# ---------------------------------------------------------------------------
def support_menu_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=sup[lang].get("btn_new"), callback_data="sup_filter:NEW")],
        [InlineKeyboardButton(text=sup[lang].get("btn_all"), callback_data="sup_filter:ALL")],
        [InlineKeyboardButton(text=gen[lang].get("back"),    callback_data="menu:main")],
    ])

def support_list_kb(lang: str, items: list, page: int, total_pages: int, status_filter: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        user_name = item.user.name if item.user else "Anonymous"
        label = f"#{item.question_id} · {user_name}"
        builder.button(text=label, callback_data=f"sup_detail:{item.question_id}")
    builder.adjust(1)

    nav = _pagination_row(lang, page, total_pages, f"sup_page:{status_filter}")
    if nav:
        builder.row(*nav)

    builder.row(InlineKeyboardButton(text=gen[lang].get("back"), callback_data="menu:support"))
    return builder.as_markup()

def support_detail_kb(lang: str, question_id: int, status: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if status == Status.NEW.value:
        builder.button(text=sup[lang].get("btn_reply"), callback_data=f"sup_reply:{question_id}")
    builder.row(InlineKeyboardButton(text=gen[lang].get("back"), callback_data="sup_filter:ALL"))
    return builder.as_markup()


# ---------------------------------------------------------------------------
# Контент
# ---------------------------------------------------------------------------
def content_menu_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cnt[lang].get("btn_faq"),          callback_data="cnt:faq:0")],
        [InlineKeyboardButton(text=cnt[lang].get("btn_general_info"),  callback_data="cnt:info:0")],
        [InlineKeyboardButton(text=gen[lang].get("back"),             callback_data="menu:main")],
    ])


# --- FAQ ---
def faq_list_kb(lang: str, items: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        question_text = item.question if item.question else "Без питання" if lang == 'ua' else 'No question'
        label = f"[{item.language.upper()}] {question_text[:40]}..."
        # Передаємо сторінку 'page', щоб Clean Chat міг повернутися назад на той самий крок
        builder.button(text=label, callback_data=f"faq_detail:{item.question_id}:{page}")
    builder.adjust(1)

    nav = _pagination_row(lang, page, total_pages, "faq_page")
    if nav:
        builder.row(*nav)

    builder.row(
        InlineKeyboardButton(text=cnt[lang].get("btn_add_faq"), callback_data="faq:add"),
        InlineKeyboardButton(text=gen[lang].get("back"),        callback_data="menu:content"),
    )
    return builder.as_markup()

def faq_detail_kb(lang: str, question_id: int, back_page: int = 0) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=gen[lang].get("edit"),   callback_data=f"faq_edit:{question_id}"),
            InlineKeyboardButton(text=gen[lang].get("delete"), callback_data=f"faq_delete:{question_id}"),
        ],
        [InlineKeyboardButton(text=gen[lang].get("back"), callback_data=f"cnt:faq:{back_page}")],
    ])

def faq_edit_fields_kb(lang: str, question_id: int) -> InlineKeyboardMarkup:
    fields = {
        "ua": [("Категорія", "category"), ("Питання", "question"), ("Відповідь", "answer")],
        "en": [("Category", "category"), ("Question", "question"), ("Answer", "answer")]
    }
    builder = InlineKeyboardBuilder()
    for label, field in fields.get(lang, fields["ua"]):
        builder.button(text=label, callback_data=f"faq_field:{question_id}:{field}")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text=gen[lang].get("back"), callback_data=f"faq_detail:{question_id}:0"))
    return builder.as_markup()


# --- Загальна інформація ---
def info_list_kb(lang: str, items: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        label = f"[{item.language.upper()}] {item.category}"
        builder.button(text=label, callback_data=f"info_detail:{item.information_id}:{page}")
    builder.adjust(1)

    nav = _pagination_row(lang, page, total_pages, "info_page")
    if nav:
        builder.row(*nav)

    builder.row(
        InlineKeyboardButton(text=cnt[lang].get("btn_add_info"), callback_data="info:add"),
        InlineKeyboardButton(text=gen[lang].get("back"),         callback_data="menu:content"),
    )
    return builder.as_markup()

def info_detail_kb(lang: str, information_id: int, back_page: int = 0) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=gen[lang].get("edit"),   callback_data=f"info_edit:{information_id}"),
            InlineKeyboardButton(text=gen[lang].get("delete"), callback_data=f"info_delete:{information_id}"),
        ],
        [InlineKeyboardButton(text=gen[lang].get("back"), callback_data=f"cnt:info:{back_page}")],
    ])

def info_edit_fields_kb(lang: str, information_id: int) -> InlineKeyboardMarkup:
    fields = {
        "ua": [("Категорія", "category"), ("Текст", "information"), 
            #    ("Фотографія", "media_message_id")
               ],
        "en": [("Category", "category"), ("Text", "information"), 
            #    ("Photo", "media_message_id")
               ],
    }
    builder = InlineKeyboardBuilder()
    for label, field in fields.get(lang, fields["ua"]):
        builder.button(text=label, callback_data=f"info_field:{information_id}:{field}")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text=gen[lang].get("back"), callback_data=f"info_detail:{information_id}:0"))
    return builder.as_markup()


# ---------------------------------------------------------------------------
# Статистика
# ---------------------------------------------------------------------------
def stats_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=sts[lang].get("btn_refresh"), callback_data="stats:refresh")],
        [InlineKeyboardButton(text=gen[lang].get("back"),        callback_data="menu:main")],
    ])


# ---------------------------------------------------------------------------
# Адміністратори
# ---------------------------------------------------------------------------
def admins_menu_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=adm[lang].get("btn_list"), callback_data="adm:list:0")],
        [InlineKeyboardButton(text=adm[lang].get("btn_add"),  callback_data="adm:add")],
        [InlineKeyboardButton(text=gen[lang].get("back"),     callback_data="menu:main")],
    ])

def admins_list_kb(lang: str, items: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        # Перевіряємо об'єкт безпосередньо через Enum
        if item.admin_privilege == AdminPrivilege.SUPERADMIN:
            privilege = adm[lang].get("privilege_superadmin", "Superadmin")
        else:
            privilege = adm[lang].get("privilege_admin", "Admin")
        
        label = f"{item.name} · {privilege}"
        builder.button(text=label, callback_data=f"adm_detail:{item.telegram_id}")
    builder.adjust(1)

    nav = _pagination_row(lang, page, total_pages, "adm_page")
    if nav:
        builder.row(*nav)

    builder.row(InlineKeyboardButton(text=gen[lang].get("back"), callback_data="menu:admins"))
    return builder.as_markup()

def admin_detail_kb(lang: str, telegram_id: int, is_superadmin_target: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if not is_superadmin_target:
        builder.button(text=adm[lang].get("btn_remove"), callback_data=f"adm_remove:{telegram_id}")
    builder.row(InlineKeyboardButton(text=gen[lang].get("back"), callback_data="adm:list:0"))
    return builder.as_markup()

def users_list_kb(lang: str, items: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for user in items:
        # Показуємо Ім'я та Телефон
        phone = user.phone_number if user.phone_number else "—"
        label = f"{user.name[:20]} ({phone})"
        builder.button(text=label, callback_data=f"adm_select:{user.telegram_id}")
    builder.adjust(1)

    nav = _pagination_row(lang, page, total_pages, "adm_select_page")
    if nav:
        builder.row(*nav)

    builder.row(InlineKeyboardButton(text=gen[lang].get("back"), callback_data="menu:admins"))
    return builder.as_markup()


# ---------------------------------------------------------------------------
# Налаштування
# ---------------------------------------------------------------------------
def settings_menu_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=sett[lang].get("btn_name"),     callback_data="set:name")],
        [InlineKeyboardButton(text=sett[lang].get("btn_phone"),    callback_data="set:phone")],
        [InlineKeyboardButton(text=sett[lang].get("btn_language"), callback_data="set:language")],
        [InlineKeyboardButton(text=gen[lang].get("back"),          callback_data="menu:main")],
    ])

def settings_language_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Українська", callback_data="set_lang:ua"),
            InlineKeyboardButton(text="English",    callback_data="set_lang:en"),
        ],
        [InlineKeyboardButton(text=gen[lang].get("back"), callback_data="menu:settings")],
    ])