import telebot
import webbrowser
import random
import requests
import sqlite3
import uuid
from datetime import datetime, timedelta
from telebot import types


bot = telebot.TeleBot('6468735792:AAHrUODVPRqaBQ96ouCom7S1XHWLDC3wpVI')


@bot.message_handler(commands=['site', 'website'])
def site(message):
    webbrowser.open('https://www.youtube.com/watch?v=lHpYyYtkmrw')


new_year_jokes = [
    "Почему ёлка не ходит в театр? Она считает, что на неё смотреть неинтересно.",
    "Чем отличается Новый год от ночи перед экзаменом? На Новый год можно подготовиться.",
    "Почему снеговики всегда хорошо настроены? Потому что у них есть отличное чувство юмора, да и всякий раз, когда им что-то не по душе, они просто меняют лицо!",
    "Как называется беспечный олень? 'Наивный-олень'!",
    "Почему у елки всегда так много друзей? Потому что она такая дружелюбная и всегда приглашает всех на свои вечеринки!",
    "Какой самый любимый напиток у Санты? 'Шоколадный -Хо-Хо-Хо-!",
    "Почему у Снегурочки всегда такой хороший настрой? Потому что она знает, что всегда есть кто-то, кто её 'снеговик' вне зависимости от погоды!",
    "Как называется самый невероятный бойцовский приём у Деда Мороза? 'Подарок-сюрприз'!",
    "Почему Снегурочка никогда не проигрывает в карточные игры? Потому что она умеет хорошо 'раздавать' улыбки!",
    "Какой у Санты любимый фильм? 'Один дома', потому что там он видит, как кто-то ещё тоже заботится о подарках!",
]

@bot.message_handler(commands=['jokes'])
def send_joke(message):
    joke = random.choice(new_year_jokes)
    bot.send_message(message.chat.id, joke)


def get_nearby_events(latitude, longitude):
    return None


@bot.message_handler(commands=['events'])
def nearby_events(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton(text="Отправить местоположение", request_location=True))

    bot.send_message(message.chat.id, 'Пожалуйста, отправьте ваше текущее местоположение для поиска ближайших событий.',
                     reply_markup=markup)


@bot.message_handler(content_types=['location'])
def handle_location(message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    events = get_nearby_events(latitude, longitude)

    if events:
        bot.send_message(message.chat.id, 'Информация о ближайших событиях:')
        for event in events:
            bot.send_message(message.chat.id, f'{event["name"]}: {event["date"]}')
    else:
        tomorrow = datetime.now() + timedelta(days=1)
        formatted_date = tomorrow.strftime('%d.%m.%Y')
        message_text = f"Ближайших ивентов не обнаружено! Отправьте запрос повторно на {formatted_date}!"
        bot.send_message(message.chat.id, message_text)


decorations = ['Гирлянда', 'Шарики', 'Снежинки', 'Звезды']


decorations_status = {}

@bot.message_handler(commands=['decorate'])
def decorate_tree(message):
    user_id = message.from_user.id

    if user_id in decorations_status:
        used_decorations = decorations_status[user_id]
        available_decorations = [deco for deco in decorations if deco not in used_decorations]
        if not available_decorations:
            bot.send_message(message.chat.id, "Поздравляем, вы смогли нарядить ёлку!")
            decorations_status.pop(user_id)
            return

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for decoration in available_decorations:
            markup.add(decoration)

        bot.send_message(message.chat.id, "Выберите, чем украсить ёлку:", reply_markup=markup)
    else:
        decorations_status[user_id] = []
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for decoration in decorations:
            markup.add(decoration)

        bot.send_message(message.chat.id, "Выберите, чем украсить ёлку:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in decorations)
def add_decoration(message):
    user_id = message.from_user.id
    chosen_decoration = message.text

    if user_id in decorations_status:
        used_decorations = decorations_status[user_id]
        if chosen_decoration in used_decorations:
            bot.send_message(message.chat.id, "Украшение уже выбрано. Пожалуйста, выберите другое украшение.")
            return

        decorations_status[user_id].append(chosen_decoration)
    else:
        decorations_status[user_id] = [chosen_decoration]

    bot.send_message(message.chat.id, f"Вы нарядили ёлку выбранным украшением: {chosen_decoration}!")

    used_decorations = decorations_status[user_id]
    available_decorations = [deco for deco in decorations if deco not in used_decorations]
    if not available_decorations:
        bot.send_message(message.chat.id, "Поздравляем, вы смогли нарядить ёлку!")
        decorations_status.pop(user_id)
@bot.message_handler(commands=['countdown'])
def new_year_countdown(message):
    now = datetime.now()
    new_year = datetime(now.year + 1, 1, 1)
    time_left = new_year - now
    days = time_left.days
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    countdown_text = (
        f"До Нового года осталось:\n"
        f"{days} дней, {hours} часов, {minutes} минут, {seconds} секунд"
    )
    bot.send_message(message.chat.id, countdown_text)


conn = sqlite3.connect('user_profiles.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    unique_id TEXT
                )''')
conn.commit()
conn.close()


users_sending_messages = {}

@bot.message_handler(commands=['send_congratulation'])
def start(message):
    user_id = message.from_user.id

    conn = sqlite3.connect('user_profiles.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        unique_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO users (user_id, username, unique_id) VALUES (?, ?, ?)", (user_id, message.from_user.username, unique_id))
        conn.commit()
    else:
        unique_id = result[2]

    conn.close()

    users_sending_messages[user_id] = {}
    bot.send_message(message.chat.id, f"Ваш уникальный идентификатор для отправки сообщений: {unique_id}\nЧтобы отправить сообщение другому пользователю, введите /send_message.")

@bot.message_handler(commands=['send_message'])
def request_recipient_id(message):
    conn = sqlite3.connect('user_profiles.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, unique_id FROM users WHERE user_id != ?", (message.from_user.id,))
    results = cursor.fetchall()
    conn.close()

    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for user_id, unique_id in results:
        markup.add(types.KeyboardButton(f"{user_id} - {unique_id}"))

    markup.add(types.KeyboardButton('Отмена'))
    bot.send_message(message.chat.id, "Выберите получателя из списка или нажмите 'Отмена':", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.split(" - ")[0].isdigit() and message.from_user.id in users_sending_messages and not users_sending_messages[message.from_user.id].get('recipient_id'))
def get_recipient_id(message):
    recipient_id = int(message.text.split(" - ")[0])

    conn = sqlite3.connect('user_profiles.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (recipient_id,))
    result = cursor.fetchone()

    if result and recipient_id != message.from_user.id:
        users_sending_messages[message.from_user.id]['recipient_id'] = recipient_id
        bot.send_message(message.chat.id, f"Введите сообщение для пользователя с ID {recipient_id}:")
    else:
        bot.send_message(message.chat.id, "Пользователь не найден или выбран неверный ID. Попробуйте снова:")

@bot.message_handler(func=lambda message: message.text == 'Отмена')
def cancel_action(message):
    users_sending_messages.pop(message.from_user.id, None)
    bot.send_message(message.chat.id, "Действие отменено. Выберите команду /send_message для отправки сообщения.")

@bot.message_handler(func=lambda message: message.from_user.id in users_sending_messages and users_sending_messages[message.from_user.id].get('recipient_id'))
def send_message_to_recipient(message):
    sender_id = message.from_user.id
    recipient_id = users_sending_messages[sender_id]['recipient_id']
    congratulation_text = message.text

    bot.send_message(recipient_id, f"Вам отправлено сообщение от пользователя с ID {sender_id}:\n{congratulation_text}")
    bot.send_message(sender_id, f"Сообщение успешно отправлено пользователю с ID {recipient_id}!")

    users_sending_messages.pop(sender_id)


@bot.message_handler(commands=['congratulation'])
def congratulation(message):
    try:
        conn = sqlite3.connect('new_year_bot.db')
        cursor = conn.cursor()

        cursor.execute("SELECT message_text FROM congratulations ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()

        if result:
            congratulation = result[0]
            bot.send_message(message.chat.id, congratulation)
        else:
            bot.send_message(message.chat.id, "Кажется, нет поздравлений в базе данных.")

        conn.close()

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при получении поздравления: {str(e)}")


@bot.message_handler(commands=['add_from_list'])
def add_from_list(message):

    conn = sqlite3.connect('new_year_bot.db')
    cursor = conn.cursor()


    congratulations_list = [
        "С наступающим Новым годом! Пусть каждый новый день приносит радость, а каждая минута наполнена смехом и улыбками!",
"Пусть Новый год принесет в ваш дом столько счастья, сколько огоньков на елке, столько тепла, сколько в праздничных печеньях, и столько любви, сколько в объятиях близких!",
"С Новым годом! Пусть ваши надежды будут такими же яркими, как салют, и исполнятся даже быстрее, чем петарды в полночь!",
"Под елкой найдется не только подарки, но и море радости, счастья и уютных моментов с близкими. С наступающим вас, родные мои!",
"Не забывайте, что самое лучшее в новогодней ночи — это не фейерверки, а искренние улыбки и теплые объятия друзей и семьи.",
"С наступающим! Пусть ваш новогодний стол будет полон вкусных блюд, а ваш дом — теплом и уютом, словно самый добрый огонек в холодную ночь!",
"Новый год — это возможность начать все с чистого листа. Даже если лист — это ваша новогодняя открытка!",
"Желаю, чтобы в Новом году вас окружали такие же яркие личности, как сверкающие огоньки на елке!",
"С наступающим! Пусть ваши мечты будут такими же большими, как горка подарков у елки, и такими же яркими, как огоньки на улице!",
"Пусть Новый год принесет в ваш дом столько радости, сколько снега в сказке, столько счастья, сколько конфет в мешке, и столько улыбок, сколько звезд на небе!",
"Не забудьте зарядить свои сердца праздничным настроением и пусть весь Новый год будет похож на лучший новогодний фильм!",
"С наступающим! Пусть ваши планы на Новый год сбудутся так легко, как шампанское распивается в эту ночь!",
"Пусть Новый год будет таким же волшебным, как детство, когда ждали чуда каждый день!",
"С Новым годом! Пусть все ваши звезды сбудутся, словно загаданные желания под бой курантов!",
"Встречайте Новый год с улыбкой! Он точно не заставит вас скучать, как никто другой!",
"Пусть Новый год будет полон приятных сюрпризов, как веселые фейерверки в небе!",
"С наступающим! Пусть в новом году у вас будет столько радостных моментов, сколько пузырьков в бокале шампанского!",
"Новый год — время, когда можно быть по-настоящему счастливым без всяких оправданий!",
"С Новым годом! Пусть каждый день нового года будет таким же волшебным, как ночь перед ним!",
"Пусть Новый год будет полон не только подарков, но и радости, добра и светлых моментов в вашей жизни!",
    ]

    for congratulation_text in congratulations_list:
        cursor.execute("INSERT INTO congratulations (message_text) VALUES (?)", (congratulation_text,))
        conn.commit()

    bot.reply_to(message, "Мы успешно сгенерировали поздравления и добавили их в базу данных!")

    conn.close()


conn = sqlite3.connect('new_year_bot.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS congratulations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_text TEXT
                )''')
conn.commit()
conn.close()

@bot.message_handler(commands=['start', 'main', 'hello'])
def main(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(
        types.KeyboardButton('/congratulation - Принять поздравление\n'),
        types.KeyboardButton('/send_congratulation - отправить поздравление\n'),
        types.KeyboardButton('/jokes - Новогодние шутки\n'),
        types.KeyboardButton('/countdown - Отсчет времени до Нового года\n'),
        types.KeyboardButton('/events - Ближайшие события\n'),
        types.KeyboardButton('/decorate - Украсить ёлку\n'),
        types.KeyboardButton('/add_from_list - создайте автоматический список поздравлений!\n'),
        types.KeyboardButton('/help - помощь\n')
    )

    welcome_text = f'Привет, {message.from_user.first_name}! Выберите действие:'
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)







@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, 'вызываем пояснительную бригаду!', parse_mode='html')



bot.infinity_polling()