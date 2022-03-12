import user_database as ud
import user_meal_database as umd
import learned_dish_database as ldd
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, Update
from telegram.ext import ConversationHandler
from utils import initial_keyboard, existing_user_keyboard
from user_class import User, user_from_dict
from meal_class import Meal
from telegram.ext import CallbackContext


def start(update: Update, context: CallbackContext) -> None:
    """
    Handler that deletes all existing records about the user and starts the dating procedure
    """
    print("Кто-то запустил бота!")
    print("Удаляю имеющуюся запись")
    ud.delete_note_with_id(update.effective_chat.id)
    umd.delete_all_meal_notes(update.effective_chat.id)
    update.message.reply_text(
        f"{update.message.chat.first_name}, Вас приветствует Foodbot. "
        f"Прежде чем начать работу, мне нужно узнать кое-что о вас. "
        f"Давайте познакомимся!",
        reply_markup=initial_keyboard(),
    )


def acquaintance(update: Update, context: CallbackContext) -> str:
    """
    Handler requesting a username
    """
    update.message.reply_text(
        "Как к Вам обращаться? Введите имя или псевдоним: ",
        reply_markup=ReplyKeyboardRemove(),
    )
    return "user_name"


def get_user_name(update: Update, context: CallbackContext) -> str:
    """
    Handler that takes a user's name and asks for user's age
    """
    context.user_data["name"] = update.message.text
    update.message.reply_text(f"{update.message.text.capitalize()}, cколько Вам лет? ")
    return "user_birth_date"


def get_user_birth_date(update: Update, context: CallbackContext) -> str:
    """
    Handler that gets the user's age and asks for user's sex
    """
    context.user_data["birth_date"] = update.message.text
    reply_keyboard = [["мужской", "женский"]]
    update.message.reply_text(
        "Укажите свой пол:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return "user_sex"


def get_user_sex(update: Update, context: CallbackContext) -> str:
    """
    Handler that gets the user's gender and asks for user's height
    """
    context.user_data["sex"] = update.message.text
    update.message.reply_text("Введите ваш рост в сантиметрах (например, 180): ")
    return "user_height"


def get_user_height(update: Update, context: CallbackContext) -> str:
    """
    Handler that receives the user's height and requests user's weight
    """
    context.user_data["height"] = update.message.text
    update.message.reply_text("Введите ваш вес в килограммах (например, 74): ")
    return "user_weight"


def get_user_weight(update: Update, context: CallbackContext) -> str:
    """
    Handler that receives the user's weight and requests user's activity level
    """
    context.user_data["weight"] = update.message.text
    reply_keyboard = [["нулевая", "слабая", "средняя", "высокая", "экстремальная"]]
    update.message.reply_text(
        "Какой у Вас уровень активности? <добавить пояснения>",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return "user_activity"


def get_user_activity(update: Update, context: CallbackContext) -> str:
    """
    Handler that gets the user's activity level and asks for the user's goal
    """
    context.user_data["activity"] = update.message.text
    reply_keyboard = [["похудение", "поддержание формы", "набор массы"]]
    update.message.reply_text(
        "Какая у вас цель? <добавить пояснения>",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return "user_goal"


def get_user_goal(update: Update, context: CallbackContext) -> int:
    """
    Handler that gets the user's user's goal and adds the created user to the user database
    """
    context.user_data["goal"] = update.message.text
    update.message.reply_text(
        f'Отлично, {context.user_data["name"].capitalize()}! '
        f"Теперь я могу подсчитать вашу норму калорий и нутриентов. "
        f"Дайте мне секунду..."
    )
    user = User(
        user_id=update.message.chat.id,
        name=context.user_data["name"],
        age=context.user_data["birth_date"],
        sex=context.user_data["sex"],
        height=context.user_data["height"],
        weight=context.user_data["weight"],
        activity=context.user_data["activity"],
        goal=context.user_data["goal"],
    )
    user.count_norm()
    update.message.reply_text(user.get_short_info())
    user.user_to_database()
    update.message.reply_text("Для продолжения взаимодействия с ботом напишите 'Go'")
    return ConversationHandler.END


def existing_user(update: Update, context: CallbackContext) -> str:
    """
    Handler waiting for user action
    """
    user_name = ud.get_user_object(user_id=update.message.chat.id)["user_name"]
    update.message.reply_text(
        f"{user_name}, я рад тебя видеть! Чем я могу тебе помочь?",
        reply_markup=existing_user_keyboard(),
    )
    return "main_state"


def get_cpfc_norm(update: Update, context: CallbackContext) -> None:
    """
    Handler that displays information about the user's daily calorie and nutrient intake
    """
    user = user_from_dict(ud.get_user_object(update.effective_chat.id))
    update.message.reply_text(user.get_short_info())


def update_existing_user_data(update: Update, context: CallbackContext) -> str:
    """
    Handler requesting what data the user wants to change
    """
    reply_keyboard = [
        ["Имя", "Возраст", "Пол"],
        ["Вес", "Рост"],
        ["Уровень активности", "Цель", "Вернуться в основное меню"],
    ]
    update.message.reply_text(
        "Какую информацию ты хочешь изменить?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return "update_existing_user_data"


def pre_update_exiting_user_name(update: Update, context: CallbackContext) -> str:
    """
    Handler requesting a changed username
    """
    update.message.reply_text("Укажите новое имя")
    return "update_exiting_user_name"


def update_exiting_user_name(update: Update, context: CallbackContext) -> str:
    """
    Handler receiving changed username
    """
    user_enter = update.message.text
    ud.update_user_name(update.effective_chat.id, user_enter)
    reply_keyboard = [["Продолжить"]]
    update.message.reply_text(
        'Для продолжения взаимодестаия с ботом нажмите "Продолжить"',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "main_state"


def pre_update_exiting_user_age(update: Update, context: CallbackContext) -> str:
    """
    Handler requesting the user's changed age
    """
    update.message.reply_text("Укажите новый возраст")
    return "update_exiting_user_age"


def update_exiting_user_age(update: Update, context: CallbackContext) -> str:
    """
    Handler that receives the user's changed age
    """
    user_enter = update.message.text
    ud.update_user_age(update.effective_chat.id, int(user_enter))
    reply_keyboard = [["Пересчитать норму каллорий"]]
    update.message.reply_text(
        "Изменения внесены",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return "update_exiting_user_norm"


def pre_update_exiting_user_sex(update: Update, context: CallbackContext) -> str:
    """
    Handler requesting a changed user's sex
    """
    reply_keyboard = [["Мужской", "Женский"]]
    update.message.reply_text(
        "Укажите новый пол:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return "update_exiting_user_sex"


def update_exiting_user_sex(update: Update, context: CallbackContext) -> str:
    """
    Handler that receives the user's changed sex
    """
    user_enter = update.message.text
    ud.update_user_sex(update.effective_chat.id, user_enter)
    reply_keyboard = [["Пересчитать норму каллорий"]]
    update.message.reply_text(
        "Изменения внесены",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "update_exiting_user_norm"


def pre_update_exiting_user_height(update: Update, context: CallbackContext) -> str:
    """
    Handler that requests the user's height to be changed
    """
    update.message.reply_text("Укажите новый рост")
    return "update_exiting_user_height"


def update_exiting_user_height(update: Update, context: CallbackContext) -> str:
    """
    Handler receiving user's modified height
    """
    user_enter = update.message.text
    ud.update_user_height(update.effective_chat.id, float(user_enter))
    reply_keyboard = [["Пересчитать норму каллорий"]]
    update.message.reply_text(
        "Изменения внесены",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "update_exiting_user_norm"


def pre_update_exiting_user_weight(update: Update, context: CallbackContext) -> str:
    """
    Handler requesting the user's changed weight
    """
    update.message.reply_text("Укажите новый вес")
    return "update_exiting_user_weight"


def update_exiting_user_weight(update: Update, context: CallbackContext) -> str:
    """
    Handler receiving user's changed weight
    """
    user_enter = update.message.text
    ud.update_user_weight(update.effective_chat.id, float(user_enter))
    reply_keyboard = [["Пересчитать норму каллорий"]]
    update.message.reply_text(
        "Изменения внесены",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "update_exiting_user_norm"


def pre_update_exiting_user_activity(update: Update, context: CallbackContext) -> str:
    """
    Handler requesting changed user activity
    """
    reply_keyboard = [["Нулевая", "Слабая", "Средняя", "Высокая", "Экстремальная"]]
    update.message.reply_text(
        "Укажите новый уровень активности",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return "update_exiting_user_activity"


def update_exiting_user_activity(update: Update, context: CallbackContext) -> str:
    """
    Handler receiving changed user activity
    """
    user_enter = update.message.text
    ud.update_user_activity(update.effective_chat.id, user_enter)
    reply_keyboard = [["Пересчитать норму каллорий"]]
    update.message.reply_text(
        "Изменения внесены",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "update_exiting_user_norm"


def pre_update_exiting_user_goal(update: Update, context: CallbackContext) -> str:
    """
    Handler requesting a modified user goal
    """
    reply_keyboard = [["Похудение", "Поддержание формы", "Набор массы"]]
    update.message.reply_text(
        "Укажите новую цель",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return "update_exiting_user_goal"


def update_exiting_user_goal(update: Update, context: CallbackContext) -> str:
    """
    The handler that receives the user's modified goal
    """
    user_enter = update.message.text
    ud.update_user_goal(update.effective_chat.id, user_enter)
    reply_keyboard = [["Пересчитать норму каллорий"]]
    update.message.reply_text(
        "Изменения внесены",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "update_exiting_user_norm"


def update_exiting_user_norm(update: Update, context: CallbackContext) -> str:
    """
    Handler that recalculates the user's daily calorie and nutrient intake
    """
    user = user_from_dict(ud.get_user_object(update.effective_chat.id))
    user.count_norm()
    ud.update_user_calorie_norm(update.effective_chat.id, user.calorie_norm)
    ud.update_user_protein_norm(update.effective_chat.id, user.protein_norm)
    ud.update_user_fat_norm(update.effective_chat.id, user.fat_norm)
    ud.update_user_carbohydrate_norm(update.effective_chat.id, user.carbohydrate_norm)
    reply_keyboard = [["Продолжить"]]
    update.message.reply_text(
        'Для продолжения взаимодестаия с ботом нажмите "Продолжить"',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "main_state"


def return_to_main_state(update: Update, context: CallbackContext) -> str:
    """
    Handler that returns the dialog to the standard state
    """
    reply_keyboard = [["Продолжить"]]
    update.message.reply_text(
        'Для продолжения взаимодестаия с ботом нажмите "Продолжить"',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "main_state"


def add_new_meal(update: Update, context: CallbackContext) -> str:
    """
    Handler requesting the name of the eaten dish
    """
    update.message.reply_text(
        "Введите название съеденного блюда",
        reply_markup=ReplyKeyboardRemove(),
    )
    return "get_meal_dish"


def get_meal_dish(update: Update, context: CallbackContext) -> str:
    """
    Handler receiving the name of the dish eaten and requesting the portion size
    """
    context.user_data["meal_dish"] = update.message.text
    dish_info = ldd.get_learned_dish_note(context.user_data["meal_dish"].lower())
    update.message.reply_text("Введите размер съеденной порции (в граммах)")
    if dish_info != {}:
        return "get_meal_size_alternative"
    else:
        return "get_meal_size"


def get_meal_size_alternative(update: Update, context: CallbackContext) -> str:
    """
    Handler receiving the name of the dish eaten and requesting the portion size
    (if the dish is in the learned_dish database)
    """
    context.user_data["meal_size"] = update.message.text
    user_name = ud.get_user_object(user_id=update.message.chat.id)["user_name"]
    update.message.reply_text(
        f"Отлично, {user_name}! " f"Я уже знаю пищевую ценность этого блюда... "
    )
    dish_info = ldd.get_learned_dish_note(context.user_data["meal_dish"])
    meal = Meal(
        user_id=update.effective_chat.id,
        meal_id=umd.generate_meal_id(update.effective_chat.id),
        dish=context.user_data["meal_dish"],
        meal_size=float(context.user_data["meal_size"]),
        average_calories=float(dish_info["learned_dish_average_calories"]),
        average_proteins=float(dish_info["learned_dish_average_proteins"]),
        average_fats=float(dish_info["learned_dish_average_fats"]),
        average_carbohydrates=float(dish_info["learned_dish_average_carbohydrates"]),
    )
    meal.meal_to_database()
    update.message.reply_text(meal.get_short_meal_info())
    reply_keyboard = [["Продолжить"]]
    update.message.reply_text(
        'Для продолжения взаимодестаия с ботом нажмите "Продолжить"',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "main_state"


def get_meal_size(update: Update, context: CallbackContext) -> str:
    """
    Handler receiving the portion size and requesting the calorie content of the dish
    """
    context.user_data["meal_size"] = update.message.text
    update.message.reply_text("Введите калорийность 100г этого блюда (в ккал)")
    return "get_meal_calories"


def get_meal_calories(update: Update, context: CallbackContext) -> str:
    """
    Handler receiving the calorie content of a meal and asking for the average amount of protein
    """
    context.user_data["meal_calories"] = update.message.text
    update.message.reply_text(
        "Введите количество белков в 100г этого блюда (в граммах)"
    )
    return "get_meal_proteins"


def get_meal_proteins(update: Update, context: CallbackContext) -> str:
    """
    Handler getting average protein and asking for average fat
    """
    context.user_data["meal_proteins"] = update.message.text
    update.message.reply_text("Введите количество жиров в 100г этого блюда (в граммах)")
    return "get_meal_fats"


def get_meal_fats(update: Update, context: CallbackContext) -> str:
    """
    Handler getting average fat and asking for average carbs
    """
    context.user_data["meal_fats"] = update.message.text
    update.message.reply_text(
        "Введите количество углеводов в 100г этого блюда (в граммах)"
    )
    return "get_meal_carbohydrates"


def get_meal_carbohydrates(update: Update, context: CallbackContext) -> str:
    """
    Handler receiving an average amount of carbohydrates and
    adding the resulting dish to the meal database
    """
    context.user_data["meal_carbohydrates"] = update.message.text
    user_name = ud.get_user_object(user_id=update.message.chat.id)["user_name"]
    update.message.reply_text(f"Отлично, {user_name}! " f"Запоминаю эту информацию... ")
    meal = Meal(
        user_id=update.effective_chat.id,
        meal_id=umd.generate_meal_id(update.effective_chat.id),
        dish=context.user_data["meal_dish"],
        meal_size=float(context.user_data["meal_size"]),
        average_calories=float(context.user_data["meal_calories"]),
        average_proteins=float(context.user_data["meal_proteins"]),
        average_fats=float(context.user_data["meal_fats"]),
        average_carbohydrates=float(context.user_data["meal_carbohydrates"]),
    )
    meal.meal_to_database()
    update.message.reply_text(meal.get_short_meal_info())
    ldd.add_learned_dish_note(
        context.user_data["meal_dish"].lower(),
        float(context.user_data["meal_calories"]),
        float(context.user_data["meal_proteins"]),
        float(context.user_data["meal_fats"]),
        float(context.user_data["meal_carbohydrates"]),
    )
    reply_keyboard = [["Продолжить"]]
    update.message.reply_text(
        'Для продолжения взаимодестаия с ботом нажмите "Продолжить"',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "main_state"


def get_statistic(update: Update, context: CallbackContext) -> str:
    """
    Handler requesting the period for which you want to display statistics
    """
    reply_keyboard = [
        ["За текущий день"],
        ["За последние 7 дней"],
        ["За последний месяц"],
    ]
    update.message.reply_text(
        "Выберите за какой промежуток времени получить статистику",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "get_statistic_for"


def get_statistic_for_day(update: Update, context: CallbackContext) -> str:
    """
    Handler displaying statistics for 1 day
    """
    user = user_from_dict(ud.get_user_object(update.effective_chat.id))
    update.message.reply_text(user.get_meal_statistic_for_day())
    reply_keyboard = [["Продолжить"]]
    update.message.reply_text(
        'Для продолжения взаимодестаия с ботом нажмите "Продолжить"',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "main_state"


def get_statistic_for_week(update: Update, context: CallbackContext) -> str:
    """
    Handler displaying statistics for last 7 days
    """
    user = user_from_dict(ud.get_user_object(update.effective_chat.id))
    update.message.reply_text(user.get_meal_statistic_for_week())
    reply_keyboard = [["Продолжить"]]
    update.message.reply_text(
        'Для продолжения взаимодестаия с ботом нажмите "Продолжить"',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "main_state"


def get_statistic_for_month(update: Update, context: CallbackContext) -> str:
    """
    Handler displaying statistics for last 31 days
    """
    user = user_from_dict(ud.get_user_object(update.effective_chat.id))
    update.message.reply_text(user.get_meal_statistic_for_month())
    reply_keyboard = [["Продолжить"]]
    update.message.reply_text(
        'Для продолжения взаимодействия с ботом нажмите "Продолжить"',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return "main_state"


def delete_last_meal_note(update: Update, context: CallbackContext) -> None:
    """
    Handler that removes the user's last meal from the meal database
    """
    umd.delete_meal_note(
        update.effective_chat.id, umd.generate_meal_id(update.effective_chat.id) - 1
    )
    update.message.reply_text("Последняя запись о приеме пищи успешно удалена")


if __name__ == "__main__":
    print(type(ConversationHandler.END))
