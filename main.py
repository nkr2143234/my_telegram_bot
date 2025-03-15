import telebot
import logging
import random
import threading
import time
import pytz
from secrets import secrets
from telebot import types
from datetime import datetime, timedelta
from collections import defaultdict

# Константы
DEFAULT_GOALS = [
    "♻️ Использовать многоразовую бутылку",
    "🚫 Отказаться от пластиковых пакетов",
    "📦 Сортировать мусор",
    "💡 Выключать свет при выходе",
    "🚲 Передвигаться экологично"
]

ECO_STATS = {
    '♻️ Использовать многоразовую бутылку': {'water': 500, 'plastic': 1},
    '🚫 Отказаться от пластиковых пакетов': {'plastic': 3},
    '📦 Сортировать мусор': {'co2': 2},
    '💡 Выключать свет при выходе': {'co2': 1},
    '🚲 Передвигаться экологично': {'co2': 5}
}

BADGES = {
    'beginner': {'threshold': 3, 'emoji': '🌱', 'name': 'Эко-Новичок', 'description': '3 дня подряд'},
    'enthusiast': {'threshold': 7, 'emoji': '🌟', 'name': 'Эко-Энтузиаст', 'description': '7 дней подряд'},
    'hero': {'threshold': 15, 'emoji': '🏆', 'name': 'Эко-Герой', 'description': '15 дней подряд'}
}

ECO_TIPS = [
    "🛍️ Носите с собой складную многоразовую сумку",
    "💧 Установите аэратор на кран для экономии воды",
    "🚲 Используйте велосипед для поездок до 5 км",
    "♻️ Собирайте батарейки в отдельный контейнер",
    "🌿 Выбирайте продукты с маркировкой Fairtrade",
    "📦 Покупайте крупы и специи на развес",
    "💡 Настройте умный термостат для экономии энергии",
    "🌳 Посадите дерево через специальные экоприложения",
    "🚰 Используйте многоразовую бутылку для воды",
    "🍎 Организуйте совместные закупки фермерских продуктов",
    "👕 Отдавайте ненужную одежду в charity shops",
    "🚗 Совмещайте поездки, чтобы сократить пробег",
    "☕ Откажитесь от пластиковых крышек для стаканов",
    "📱 Сдавайте старую технику на переработку",
    "🚮 Организуйте раздельный сбор в своем подъезде",
    "🌞 Установите солнечные батареи на балконе",
    "🧴 Выбирайте косметику с эко-сертификатами",
    "📚 Берите книги в библиотеке вместо покупки",
    "🍃 Используйте бамбуковые зубные щетки",
    "🚿 Принимайте душ вместо ванны"
]

TIP_CATEGORIES = {
    '🏠 Дом': [
        "♻️ Установите компостер для органических отходов",
        "💡 Замените все лампочки на светодиодные",
        "🚰 Поставьте фильтр для воды вместо покупки бутилированной",
        "🌡️ Утеплите окна для снижения теплопотерь"
    ],
    '🛒 Покупки': [
        "🛍️ Используйте экомешочки для овощей и фруктов",
        "🍴 Откажитесь от одноразовой пластиковой посуды",
        "📅 Составляйте список покупок заранее",
        "🌱 Выбирайте продукты в биоразлагаемой упаковке"
    ],
    '🚗 Транспорт': [
        "🚌 Пользуйтесь каршерингом вместо личного авто",
        "🚶 Пройдите пешком 10 000 шагов в день",
        "⚡ Рассмотрите электромобиль для следующей покупки",
        "🗺️ Планируйте маршрут для сокращения пробега"
    ],
    '💡 Энергия': [
        "🔌 Используйте умные розетки с таймером",
        "❄️ Установите температуру кондиционера на 24°C",
        "☀️ Сушите белье естественным образом",
        "🔋 Установите систему накопления энергии"
    ],
    '🍎 Питание': [
        "🍽️ Готовьте порции разумного размера",
        "🥕 Используйте остатки еды для новых блюд",
        "📆 Планируйте меню на неделю вперед",
        "🌱 Раз в неделю устраивайте вегетарианский день"
    ],
    '💧 Вода': [
        "🚿 Сократите время душа до 5 минут",
        "🌧️ Установите бочку для сбора дождевой воды",
        "🚰 Чините протечки сразу после обнаружения",
        "🪣 Используйте воду после мытья овощей для полива"
    ],
    '👗 Мода': [
        "👖 Покупайте качественную одежду на вторичном рынке",
        "🧵 Организуйте ремонтную мастерскую для одежды",
        "🔄 Участвуйте в своп-вечеринках",
        "🎒 Выбирайте сумки из переработанных материалов"
    ],
    '🌳 Природа': [
        "🌲 Участвуйте в посадке городских садов",
        "🐝 Установите отель для насекомых на балконе",
        "🌸 Сажайте местные виды растений",
        "🗑️ Организуйте субботник в своем районе"
    ],
    '📱 Технологии': [
        "📡 Отключайте роутер на ночь",
        "🔋 Используйте режим энергосбережения на устройствах",
        "🖥️ Выбирайте технику с высоким классом энергоэффективности",
        "☁️ Ограничьте использование облачных хранилищ"
    ],
    '👶 Дети': [
        "🧸 Покупайте игрушки из натуральных материалов",
        "📚 Выбирайте многоразовые подгузники",
        "🎨 Организуйте творческие мастер-классы из вторсырья",
        "🚸 Создайте экологичный набор для пикника"
    ]
}

# Инициализация бота
token = secrets.get('BOT_API_TOKEN')
bot = telebot.TeleBot(token)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

# Хранилище данных пользователей
users_data = {}


class UserData:
    def __init__(self):
        self.goals = []
        self.adding_goal = False
        self.deleting_goal = False
        self.notifications_enabled = True
        self.notification_time = "10:00"
        self.total_water = 0
        self.total_co2 = 0
        self.total_plastic = 0
        self.progress_history = []
        self.badges = []
        self.last_tip_date = None
        self.preferred_categories = list(TIP_CATEGORIES.keys())
        self.units = 'metric'

    def update_stats(self, goal_text):
        stats = ECO_STATS.get(goal_text, {})
        self.total_water += stats.get('water', 0)
        self.total_co2 += stats.get('co2', 0)
        self.total_plastic += stats.get('plastic', 0)

        today = datetime.now().date()
        if today not in self.progress_history:
            self.progress_history.append(today)

        return self.check_badges()

    def check_badges(self):
        new_badges = []
        consecutive_days = self.get_consecutive_days()
        for badge_id, params in BADGES.items():
            if (badge_id not in self.badges and
                    consecutive_days >= params['threshold']):
                self.badges.append(badge_id)
                new_badges.append(params)
        return new_badges

    def get_consecutive_days(self):
        if not self.progress_history:
            return 0

        unique_dates = sorted(list(set(self.progress_history)))
        current_streak = 1
        max_streak = 1

        for i in range(1, len(unique_dates)):
            if (unique_dates[i] - unique_dates[i - 1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        return max_streak


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("🚀 СТАРТ"))
    markup.row(
        types.KeyboardButton("🌱 Мои цели"),
        types.KeyboardButton("📌 Совет дня")
    )
    markup.row(
        types.KeyboardButton("📊 Прогресс"),
        types.KeyboardButton("⚙️ Настройки")
    )
    markup.row(types.KeyboardButton("📚 Информация"))
    return markup


def goals_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton("➕ Добавить цель"),
        types.KeyboardButton("📝 Мои текущие цели"),
        types.KeyboardButton("✅ Отметить выполнение"),
        types.KeyboardButton("❌ Удалить цель"),
        types.KeyboardButton("🔙 Назад")
    ]
    markup.add(*buttons)
    return markup


def tips_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton("🎲 Случайный совет"),
        types.KeyboardButton("📚 Все советы по категориям"),
        types.KeyboardButton("🔙 Назад")
    ]
    markup.add(*buttons)
    return markup


def settings_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton("🕒 Время уведомлений"),
        types.KeyboardButton("🔔 Уведомления Вкл/Выкл"),
        types.KeyboardButton("📏 Единицы измерения"),
        types.KeyboardButton("💡 Категории советов"),
        types.KeyboardButton("🔙 Назад")
    ]
    markup.add(*buttons)
    return markup


@bot.message_handler(commands=['start'])
def start_message(message):
    users_data[message.chat.id] = UserData()
    bot.send_message(
        message.chat.id,
        text=f"Привет, {message.from_user.first_name}! 👋",
        reply_markup=main_menu())


@bot.message_handler(func=lambda msg: msg.text == "🚀 СТАРТ")
def start_button_handler(message):
    text = (
        "🌍 *ЭкоПомощник* 🌿\n\n"
        "Я помогу тебе:\n"
        "✅ Отслеживать экологические привычки\n"
        "🏆 Зарабатывать награды за последовательность\n"
        "📈 Видеть свой экологический вклад\n\n"
        "Начни с выбора целей в разделе '🌱 Мои цели'!"
    )
    bot.send_message(message.chat.id,
                     text=text,
                     parse_mode='Markdown',
                     reply_markup=main_menu())


@bot.message_handler(func=lambda msg: msg.text == "🌱 Мои цели")
def goals_handler(message):
    user_data = users_data.setdefault(message.chat.id, UserData())

    if not user_data.goals:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = [types.KeyboardButton(goal) for goal in DEFAULT_GOALS]
        buttons.append(types.KeyboardButton("➕ Создать свою цель"))
        buttons.append(types.KeyboardButton("🔙 Назад"))
        markup.add(*buttons)

        bot.send_message(
            message.chat.id,
            "🌟 Рекомендуемые цели для старта:\nВыберите готовый вариант или создайте свою!",
            reply_markup=markup
        )
    else:
        bot.send_message(message.chat.id,
                         "Управление вашими целями:",
                         reply_markup=goals_menu())


@bot.message_handler(func=lambda msg: msg.text in ["➕ Добавить цель", "➕ Создать свою цель"])
def add_goal_handler(message):
    users_data[message.chat.id].adding_goal = True
    markup = types.ForceReply(selective=False)
    bot.send_message(message.chat.id,
                     "✏️ Введите свою цель:",
                     reply_markup=markup)


@bot.message_handler(func=lambda msg: users_data.get(msg.chat.id, UserData()).adding_goal)
def process_new_goal(message):
    try:
        user_data = users_data[message.chat.id]
        user_data.adding_goal = False
        goal_text = message.text.strip()

        if not goal_text:
            bot.send_message(message.chat.id,
                             "❌ Нельзя добавить пустую цель",
                             reply_markup=goals_menu())
            return

        if any(g["text"].lower() == goal_text.lower() for g in user_data.goals):
            bot.send_message(message.chat.id,
                             "❌ Эта цель уже существует!",
                             reply_markup=goals_menu())
            return

        new_goal = {
            "text": goal_text,
            "created": datetime.now().strftime("%d.%m.%Y"),
            "progress": 0
        }

        user_data.goals.append(new_goal)
        bot.send_message(message.chat.id,
                         f"✅ Цель добавлена: {new_goal['text']}",
                         reply_markup=goals_menu())

    except Exception as e:
        logging.error(f"Ошибка добавления цели: {str(e)}")
        bot.send_message(message.chat.id,
                         "⚠️ Произошла ошибка при добавлении цели",
                         reply_markup=main_menu())


@bot.message_handler(func=lambda msg: msg.text in DEFAULT_GOALS)
def add_default_goal(message):
    user_data = users_data[message.chat.id]
    new_goal = {
        "text": message.text,
        "created": datetime.now().strftime("%d.%m.%Y"),
        "progress": 0
    }
    user_data.goals.append(new_goal)
    bot.send_message(message.chat.id,
                     f"✅ Цель добавлена: {new_goal['text']}",
                     reply_markup=goals_menu())


@bot.message_handler(func=lambda msg: msg.text == "📝 Мои текущие цели")
def show_goals_handler(message):
    user_data = users_data.get(message.chat.id, UserData())
    if not user_data.goals:
        bot.send_message(message.chat.id,
                         "📭 У вас пока нет активных целей",
                         reply_markup=goals_menu())
        return

    goals_text = "📋 Ваши текущие цели:\n\n"
    for i, goal in enumerate(user_data.goals, 1):
        goals_text += (f"{i}. {goal['text']}\n"
                       f"   📅 Добавлена: {goal['created']}\n"
                       f"   🏆 Прогресс: {goal['progress']} дней\n\n")

    bot.send_message(message.chat.id, goals_text)


@bot.message_handler(func=lambda msg: msg.text == "✅ Отметить выполнение")
def mark_progress_handler(message):
    user_data = users_data.get(message.chat.id, UserData())
    if not user_data.goals:
        bot.send_message(message.chat.id,
                         "📭 Сначала добавьте цели!",
                         reply_markup=goals_menu())
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for goal in user_data.goals:
        markup.add(types.KeyboardButton(f"✅ {goal['text']}"))
    markup.add(types.KeyboardButton("🔙 Назад"))

    bot.send_message(message.chat.id,
                     "Выберите цель для отметки:",
                     reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text.startswith("✅"))
def process_progress_marking(message):
    try:
        if ' ' not in message.text:
            raise ValueError("Некорректный формат цели")

        goal_text = message.text.split(' ', 1)[1].strip()
        user_data = users_data[message.chat.id]
        response = ""

        for goal in user_data.goals:
            if goal["text"] == goal_text:
                goal["progress"] += 1
                new_badges = user_data.update_stats(goal_text)

                response = (f"🎉 Прогресс обновлен!\n"
                            f"Цель: {goal_text}\n"
                            f"Всего дней: {goal['progress']}\n"
                            f"🔥 Текущая серия: {user_data.get_consecutive_days()} дней")

                if new_badges:
                    badges_text = "\n\n🎖 Новые достижения:\n" + "\n".join(
                        [f"{b['emoji']} {b['name']} - {b['description']}" for b in new_badges])
                    response += badges_text
                    for badge in new_badges:
                        bot.send_message(
                            message.chat.id,
                            f"🏅 *Новый бейдж!*\n"
                            f"{badge['emoji']} *{badge['name']}*\n"
                            f"_{badge['description']}_",
                            parse_mode='Markdown'
                        )

                bot.send_message(message.chat.id, response, reply_markup=goals_menu())
                return

        bot.send_message(message.chat.id,
                         f"❌ Цель '{goal_text}' не найдена",
                         reply_markup=goals_menu())

    except Exception as e:
        logging.error(f"Ошибка отметки выполнения: {str(e)}")
        bot.send_message(message.chat.id,
                         "⚠️ Произошла ошибка при обработке запроса",
                         reply_markup=main_menu())


@bot.message_handler(func=lambda msg: msg.text == "❌ Удалить цель")
def delete_goal_handler(message):
    user_data = users_data.get(message.chat.id, UserData())

    if not user_data.goals:
        bot.send_message(message.chat.id,
                         "🗑 Нет целей для удаления",
                         reply_markup=goals_menu())
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for goal in user_data.goals:
        markup.add(types.KeyboardButton(f"❌ {goal['text']}"))
    markup.add(types.KeyboardButton("🔙 Назад"))

    user_data.deleting_goal = True
    bot.send_message(message.chat.id,
                     "Выберите цель для удаления:",
                     reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text.startswith("❌ "))
def process_goal_deletion(message):
    user_data = users_data[message.chat.id]
    goal_text = message.text[2:]

    for i, goal in enumerate(user_data.goals):
        if goal['text'] == goal_text:
            del user_data.goals[i]
            bot.send_message(
                message.chat.id,
                f"🗑 Цель удалена: {goal_text}",
                reply_markup=goals_menu()
            )
            user_data.deleting_goal = False
            return

    bot.send_message(message.chat.id,
                     "❌ Цель не найдена",
                     reply_markup=goals_menu())


@bot.message_handler(func=lambda msg: msg.text == "📊 Прогресс")
def progress_handler(message):
    user_data = users_data.get(message.chat.id, UserData())

    stats_text = (
        "🌍 *Общая статистика*\n\n"
        f"💧 Сэкономлено воды: {user_data.total_water} л\n"
        f"🌳 Сокращено CO2: {user_data.total_co2} кг\n"
        f"🛍️ Не использовано пластика: {user_data.total_plastic} шт\n"
    )

    week_progress = sum(1 for d in user_data.progress_history
                        if d > datetime.now().date() - timedelta(days=7))
    progress_bar = "🟢" * week_progress + "⚪️" * (7 - week_progress)
    viz_text = (
        "\n📈 *Прогресс за неделю*\n"
        f"{progress_bar}\n"
        f"Выполнено дней: {week_progress}/7\n"
    )

    streak_text = (
        f"\n🔥 Текущая серия: {user_data.get_consecutive_days()} дней подряд\n"
    )

    badges_text = "\n🏆 *Доступные награды*\n"
    for badge_id, params in BADGES.items():
        status = "✅" if badge_id in user_data.badges else "◻️"
        badges_text += (
            f"{params['emoji']} {params['name']} - {params['description']} {status}\n"
        )

    advice_text = generate_advice(user_data)

    full_text = stats_text + viz_text + streak_text + badges_text + advice_text
    bot.send_message(message.chat.id,
                     full_text,
                     parse_mode='Markdown',
                     reply_markup=main_menu())


def generate_advice(user_data):
    if not user_data.goals:
        return "\n\n💡 Совет: Начните с добавления первой цели!"

    goal_stats = defaultdict(int)
    for goal in user_data.goals:
        for day in user_data.progress_history[-7:]:
            goal_stats[goal['text']] += 1

    advice = []

    if goal_stats:
        least_common = min(goal_stats, key=goal_stats.get)
        if goal_stats[least_common] < 2:
            advice.append(f"💡 Попробуйте чаще выполнять цель '{least_common}'")

    if user_data.total_plastic < 10:
        advice.append("🛍️ Используйте многоразовые сумки вместо пластиковых пакетов")
    if user_data.total_water < 2000:
        advice.append("💧 Установите аэратор на кран для экономии воды")
    if user_data.total_co2 < 15:
        advice.append("🌳 Попробуйте чаще ходить пешком или ездить на велосипеде")

    return "\n\n🌟 Советы:\n" + "\n".join(advice) if advice else "\n\n🎉 Вы молодец! Продолжайте в том же духе!"


@bot.message_handler(func=lambda msg: msg.text == "📚 Информация")
def info_handler(message):
    text = (
        "📚 *ИНФОРМАЦИЯ*\n\n"
        "🌍 *О проекте*\n"
        "Чат-бот «ЭкоПомощник» — ваш персональный гид в мире осознанного потребления. Мы помогаем:\n"
        "- Формировать экологические привычки через микро-действия\n"
        "- Отслеживать личный прогресс в реальных эквивалентах (вода, CO₂, пластик)\n"
        "- Получать научно обоснованные рекомендации\n"
        "- Участвовать в глобальном движении за устойчивое развитие\n\n"
        "Проект основан на принципах Целей устойчивого развития ООН (SDGs) и данных исследований WWF.\n\n"

        "🛠️ *Как это работает*\n"
        "1. *Выбор целей*\n"
        "   - 5 готовых экопривычек для старта\n"
        "   - Возможность создавать свои цели\n"
        "2. *Ежедневное использование*\n"
        "   - Уведомления в выбранное время (по умолчанию: 10:00)\n"
        "   - Быстрая отметка выполнения\n"
        "3. *Аналитика*\n"
        "   - Еженедельные отчеты\n"
        "   - Визуализация сэкономленных ресурсов\n\n"

        "📖 *Образовательные ресурсы*\n"
        "Рекомендуем к изучению:\n"
        "- Курс «Основы экологической грамотности»: https://stepik.org/экология\n"
        "- Документальный сериал «Наша планета» (Netflix)\n"
        "- Книга «Жизнь без пластика» (У. МакКаллум)\n\n"

        "⚙️ *Техническая поддержка*\n"
        "Часы работы: Пн-Пт 09:00–18:00 (МСК)\n"
        "Каналы связи:\n"
        "- Email: support@ecohelper.ru\n"
        "- Telegram: @ecohelper_support_bot\n"
        "- Форма обратной связи в меню бота\n\n"

        "♻️ *Ваши действия сегодня — чистая планета завтра!*"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')


@bot.message_handler(func=lambda msg: msg.text == "📌 Совет дня")
def daily_tip_handler(message):
    user_data = users_data.get(message.chat.id, UserData())
    today = datetime.now().date()

    if not hasattr(user_data, 'last_tip_date') or user_data.last_tip_date != today:
        user_data.last_tip_date = today
        tip = random.choice(ECO_TIPS)
        response = f"🌟 *Совет дня:*\n\n{tip}"
    else:
        response = "📌 Вы уже получали совет сегодня. Вот дополнительный совет:\n\n" + random.choice(ECO_TIPS)

    bot.send_message(message.chat.id,
                     response,
                     parse_mode='Markdown',
                     reply_markup=tips_menu())


@bot.message_handler(func=lambda msg: msg.text == "🎲 Случайный совет")
def random_tip_handler(message):
    category = random.choice(list(TIP_CATEGORIES.keys()))
    tip = random.choice(TIP_CATEGORIES[category])
    response = f"🎲 *Совет из категории {category}:*\n\n{tip}"
    bot.send_message(message.chat.id,
                     response,
                     parse_mode='Markdown',
                     reply_markup=tips_menu())


@bot.message_handler(func=lambda msg: msg.text == "📚 Все советы по категориям")
def all_tips_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for category in TIP_CATEGORIES:
        buttons.append(types.InlineKeyboardButton(
            text=category,
            callback_data=f"tips_{category}"))
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton(
        text="❌ Закрыть",
        callback_data="close_tips"))

    bot.send_message(message.chat.id,
                     "🌍 Выберите категорию экосоветов:",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('tips_'))
def category_tips_handler(call):
    category = call.data[5:]
    tips = TIP_CATEGORIES.get(category, [])

    if not tips:
        bot.answer_callback_query(call.id, "Категория не найдена")
        return

    tips_text = f"📗 *Советы: {category}*\n\n" + "\n".join(f"▫️ {tip}" for tip in tips)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=tips_text,
                          parse_mode='Markdown',
                          reply_markup=None)


@bot.callback_query_handler(func=lambda call: call.data == "close_tips")
def close_tips_handler(call):
    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.message_id)


@bot.message_handler(func=lambda msg: msg.text == "⚙️ Настройки")
def settings_handler(message):
    user_data = users_data.get(message.chat.id, UserData())
    status = "ВКЛ" if user_data.notifications_enabled else "ВЫКЛ"
    units = "Метрические (кг, литры)" if user_data.units == 'metric' else "Имперские (фунты, галлоны)"

    text = (
        f"⚙️ Текущие настройки:\n\n"
        f"🔔 Уведомления: {status}\n"
        f"🕒 Время уведомлений: {user_data.notification_time}\n"
        f"📏 Система мер: {units}\n"
        f"💡 Активные категории советов: {len(user_data.preferred_categories)}"
    )
    bot.send_message(message.chat.id, text, reply_markup=settings_menu())


@bot.message_handler(func=lambda msg: msg.text == "🕒 Время уведомлений")
def change_time_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    times = ["08:00", "10:00", "12:00", "15:00", "18:00", "Другое время"]
    markup.add(*[types.KeyboardButton(t) for t in times])
    markup.add(types.KeyboardButton("🔙 Назад"))
    bot.send_message(message.chat.id,
                     "Выберите удобное время для уведомлений:",
                     reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text == "Другое время")
def custom_time_handler(message):
    msg = bot.send_message(message.chat.id,
                           "Введите время в формате ЧЧ:ММ (например, 09:30):",
                           reply_markup=types.ForceReply())
    bot.register_next_step_handler(msg, process_custom_time)


def process_custom_time(message):
    try:
        datetime.strptime(message.text, "%H:%M")
        users_data[message.chat.id].notification_time = message.text
        bot.send_message(message.chat.id,
                         f"✅ Время уведомлений установлено на {message.text}",
                         reply_markup=settings_menu())
    except ValueError:
        bot.send_message(message.chat.id,
                         "❌ Неверный формат времени. Используйте ЧЧ:ММ",
                         reply_markup=settings_menu())


@bot.message_handler(func=lambda msg: msg.text in ["08:00", "10:00", "12:00", "15:00", "18:00"])
def preset_time_handler(message):
    users_data[message.chat.id].notification_time = message.text
    bot.send_message(message.chat.id,
                     f"✅ Время уведомлений установлено на {message.text}",
                     reply_markup=settings_menu())


@bot.message_handler(func=lambda msg: msg.text == "🔔 Уведомления Вкл/Выкл")
def toggle_notifications_handler(message):
    user_data = users_data.get(message.chat.id, UserData())
    user_data.notifications_enabled = not user_data.notifications_enabled
    status = "ВКЛ" if user_data.notifications_enabled else "ВЫКЛ"
    bot.send_message(message.chat.id,
                     f"🔔 Уведомления теперь {status}",
                     reply_markup=settings_menu())


@bot.message_handler(func=lambda msg: msg.text == "📏 Единицы измерения")
def units_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.KeyboardButton("📏 Метрическая система"),
        types.KeyboardButton("📐 Имперская система")
    ]
    markup.add(*buttons)
    bot.send_message(message.chat.id,
                     "Выберите систему измерений:",
                     reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text in ["📏 Метрическая система", "📐 Имперская система"])
def set_units_handler(message):
    user_data = users_data[message.chat.id]
    user_data.units = 'metric' if "Метрическая" in message.text else 'imperial'
    bot.send_message(message.chat.id,
                     f"✅ Система измерений изменена на {message.text}",
                     reply_markup=settings_menu())


@bot.message_handler(func=lambda msg: msg.text == "💡 Категории советов")
def tip_categories_handler(message):
    user_data = users_data[message.chat.id]
    markup = types.InlineKeyboardMarkup(row_width=2)
    for category in TIP_CATEGORIES:
        status = "✅" if category in user_data.preferred_categories else "❌"
        markup.add(types.InlineKeyboardButton(
            text=f"{status} {category}",
            callback_data=f"toggle_{category}"))
    bot.send_message(message.chat.id,
                     "Выберите интересующие категории советов:",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('toggle_'))
def toggle_category_handler(call):
    category = call.data[7:]
    user_data = users_data[call.message.chat.id]

    if category in user_data.preferred_categories:
        user_data.preferred_categories.remove(category)
    else:
        user_data.preferred_categories.append(category)

    bot.answer_callback_query(call.id, "Настройки сохранены!")
    tip_categories_handler(call.message)


def send_daily_notifications():
    while True:
        try:
            now = datetime.now(pytz.timezone('Europe/Moscow')).strftime("%H:%M")
            for chat_id, user_data in users_data.items():
                if (user_data.notifications_enabled and
                        user_data.notification_time == now and
                        datetime.now().weekday() < 5):
                    goals_status = "\n".join([f"• {g['text']}" for g in
                                              user_data.goals]) if user_data.goals else "Добавьте первую цель в разделе '🌱 Мои цели'"
                    text = (
                        f"🌞 Доброе утро! Пора выполнить экопривычки:\n\n"
                        f"{goals_status}\n\n"
                        f"Не забудьте отметить выполнение в разделе целей!"
                    )
                    bot.send_message(chat_id, text)
        except Exception as e:
            logging.error(f"Ошибка отправки уведомления: {str(e)}")
        time.sleep(60)


@bot.message_handler(func=lambda msg: msg.text == "🔙 Назад")
def back_handler(message):
    bot.send_message(message.chat.id,
                     "Главное меню:",
                     reply_markup=main_menu())


if __name__ == "__main__":
    notification_thread = threading.Thread(target=send_daily_notifications)
    notification_thread.daemon = True
    notification_thread.start()
    bot.infinity_polling(none_stop=True, interval=0)