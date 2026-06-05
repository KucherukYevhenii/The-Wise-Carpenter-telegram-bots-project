from aiogram.fsm.state import StatesGroup, State

class Registration(StatesGroup):
    """Стани для реєстрації"""
    choosing_language = State()  # вибір мови
    entering_name = State()     # введення імені
    entering_phone = State()    # введення номеру телефона
    choosing_role = State()


class SettingsStates(StatesGroup):
    '''Стани для налаштувань'''
    waiting_for_new_name = State() # введення імені
    waiting_for_new_phone = State() # введення номеру телефона

    messages_to_delete = State()


class QSTStates(StatesGroup):
    """Стани для задання питань"""
    waiting_for_question = State()
    waiting_for_confirmation = State()
    messages_to_delete = State()

class WorkshopStates(StatesGroup):
    """Стани для збереження повідомлень для видалення"""
    messages_to_delete = State()


class QuestionnaireStates(StatesGroup):
    main_menu = State()      # Головне меню (Нова, Продовжити, Архів)
    filling_form = State()   # Екран самої анкети (панель з кнопками ✅/❌)
    
    # Стани очікування тексту для кожного поля окремо
    input_country = State()  
    input_region = State()
    input_city = State()
    input_church = State()
    input_info = State()
    
    confirm_delete = State() # Очікування підтвердження видалення


class MobileQuestionnaireStates(StatesGroup):
    menu = State()
    filling_form = State()
    input_country = State()
    input_region = State()
    input_city = State()
    input_organization = State() # Нове поле
    input_purpose = State()