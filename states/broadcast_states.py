"""
FSM стани для системи розсилок
"""

from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    """Стани для створення розсилки"""
    
    # Етапи створення розсилки згідно ТЗ
    waiting_for_message = State()      # Очікування тексту/медіа від адміна
    selecting_audience = State()       # Вибір сегменту (усі/купили_курс/неактивні_7д)  
    selecting_schedule = State()       # Тип: одноразова/регулярна + час
    confirming_broadcast = State()     # Підтвердження перед відправкою
    
    # Додаткові стани для планування
    waiting_for_datetime = State()     # Очікування дати-часу для одноразової
    selecting_recurring = State()      # Вибір типу регулярної розсилки
    waiting_for_cron = State()         # Очікування CRON для регулярної
    
    # Стани для редагування (повертають прямо до підтвердження)
    editing_message = State()          # Редагування тексту
    editing_audience = State()         # Редагування аудиторії
    editing_schedule = State()         # Редагування планування
    editing_datetime = State()         # Редагування дати-часу
    editing_recurring = State()        # Редагування регулярності
    editing_cron = State()             # Редагування CRON


class UserManagementStates(StatesGroup):
    """Стани для управління користувачами"""
    
    # Пошук користувачів
    searching_user = State()           # Очікування ID або username для пошуку
    
    # Дії з користувачами  
    sending_message = State()          # Відправка повідомлення користувачу
    granting_course = State()          # Видача курсу користувачу 