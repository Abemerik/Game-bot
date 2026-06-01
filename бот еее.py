import telebot
import time
import random
import logging
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler


db = sqlite3.connect('BaseBot.db')

c = db.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    points INTEGER DEFAULT 0,
    victory INTEGER DEFAULT 0,
    defeat INTEGER DEFAULT 0,
    referals INTEGER DEFAULT 0,
    donat INTEGER DEFAULT 0
)

''')
db.commit()
c.execute('''CREATE TABLE IF NOT EXISTS vip (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    vip TEXT,
    vip_pluse TEXT
)
''')
db.commit()

c.execute('''CREATE TABLE IF NOT EXISTS admin (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    rank TEXT,
    otvet INTEGER DEFAULT 0
)
''')
db.commit()

def new_stolb(chat_id):
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()
    c.execute("ALTER TABLE users ADD COLUMN donat INTEGER DEFAULT 0;")
    db.commit()
    db.close() #добавлять новые стобики в базу
    
def get_or_create_user(user):
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user.id,))
    data = c.fetchone()
    if data is None:
        c.execute(
            "INSERT INTO users (user_id, username, first_name, last_name, points, victory, defeat, referals, donat) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user.id, user.username, user.first_name, user.last_name, 100, 0, 0, 0, 0)
        )
        db.commit()
    db.close()


bot = telebot.TeleBot('')#тут токен
admin_chat_id = #тут айди главного админа
admins_id = [] # тут айди всех админов
main_admins_id = [] # тут тоже айди старших админов
promocod = [] #тут промокоды

bot_id = None
try:
    bot_id = bot.get_me().id
except:
    pass

def admins_plata():
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()
    # Получаем все user_id из таблицы admin
    c.execute("SELECT user_id FROM admin")
    user_ids = c.fetchall()
    # Обновляем points для каждого user_id
    for (user_id,) in user_ids:
        c.execute("UPDATE users SET points = points + 100 WHERE user_id = ?", (user_id,))
    db.commit()
    db.close()



scheduler = BackgroundScheduler()
scheduler.add_job(admins_plata, 'cron', hour=12, minute=10)
scheduler.start()

admins_plata()

@bot.message_handler(commands=['ref'])
def process_ref_link(message):
    user = message.from_user
    chat_id = message.chat.id
    send_ref_link(user, chat_id)

def send_ref_link(user, chat_id):
    get_or_create_user(user)
    bot_username = 'kazbotino_bot'  # вставьте сюда ваше имя бота
    ref_link = f"https://t.me/{bot_username}?start=ref_{user.id}"
    bot.send_message(chat_id, f"Ваша реферальная ссылка:\n{ref_link}")

@bot.message_handler(commands=['start', 'menu'])
def process_handle_start(message):
    user = message.from_user
    chat_id = message.chat.id
    handle_start(message, user, chat_id)

def handle_start(message, user, chat_id):
    # Создаём пользователя, если его ещё нет
    get_or_create_user(user)
    
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].split('_')[1])
            if referrer_id != user.id:
                conn = sqlite3.connect('BaseBot.db')
                c = conn.cursor()

                # Проверяем, есть ли такой пользователь
                c.execute("SELECT user_id FROM users WHERE user_id=?", (user.id,))
                existing_user = c.fetchone()

                # Проверяем, есть ли рефералы у реферера, и увеличиваем их количество
                c.execute("SELECT referals FROM users WHERE user_id=?", (referrer_id,))
                data = c.fetchone()
                referals_count = data[0] if data and data[0] is not None else 0

                # Проверяем, не является ли пользователь уже рефералом реферера
                c.execute("SELECT referals FROM users WHERE user_id=?", (referrer_id,))
                referals_data = c.fetchone()
                # Предположим, что это число — количество рефералов
                # Тогда проверка, есть ли он там — не нужна, т.к. мы увеличиваем только число
                # Можно также хранить список рефералов, если нужно

                # Обновляем количество рефералов
                c.execute("UPDATE users SET referals = ? WHERE user_id=?", (referals_count + 1, referrer_id))
                
                # Начисляем 500 монет рефереру
                c.execute("SELECT points FROM users WHERE user_id=?", (referrer_id,))
                points_data = c.fetchone()
                current_points = points_data[0] if points_data else 0
                c.execute("UPDATE users SET points=? WHERE user_id=?", (current_points + 500, referrer_id))
                conn.commit()

                # Отправляем сообщение рефереру
                try:
                    bot.send_message(referrer_id, "🎉 Вы получили 500 монет за приглашенного друга!")
                except:
                    pass
        except Exception as e:
            print(f"Ошибка при обработке реферала: {e}")

    # вызываем основную функцию стартовой логики
    start_game(user, chat_id)

#@bot.message_handler(commands=['start', 'menu'])
def start_command(message):
    user = message.from_user
    chat_id = message.chat.id
    start_game(user, chat_id)

def start_game(user, chat_id):
    username = user.first_name
    user_id = user.id
    #new_stolb(chat_id) #добавлять новые стобики в базу
    get_or_create_user(user)
    

    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()

    c.execute("SELECT points, victory, defeat, referals FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()  

    points, victory, defeat, referals = result

    c.execute("SELECT * FROM admin WHERE user_id=?", (user.id,))
    data = c.fetchone()

    if data is not None:
        c.execute("SELECT rank, otvet FROM admin WHERE user_id=?", (user_id,))
        result = c.fetchone()
        rank, otvet = result
        db.close()
    else:
        pass
    
    #if user.id in main_admins_id:
    #    rank = "Главный администратор"
    #else:
    #    rank = "Администратор"
    if data is not None:
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn_1 = telebot.types.InlineKeyboardButton(text="Играть кубик", callback_data="cube_adm")
        btn_2 = telebot.types.InlineKeyboardButton(text="Играть слоты", callback_data="slot_adm")
        btn_3 = telebot.types.InlineKeyboardButton(text="Поддержка", callback_data="help_adm")
        btn_4 = telebot.types.InlineKeyboardButton(text="Промокод", callback_data="promo_adm")
        btn_6 = telebot.types.InlineKeyboardButton(text="Заблокировать", callback_data="ban")
        btn_7 = telebot.types.InlineKeyboardButton(text="Добавить админа", callback_data="adm+")
        btn_8 = telebot.types.InlineKeyboardButton(text="Уволить админа", callback_data="adm-")
        btn_9 = telebot.types.InlineKeyboardButton(text="Добавить промокод", callback_data="promo+")
        btn_10 = telebot.types.InlineKeyboardButton(text="Убрать промокод", callback_data="promo-")
        btn_11 = telebot.types.InlineKeyboardButton(text="Репорты", callback_data="rep_adm")
        btn_12 = telebot.types.InlineKeyboardButton(text="Группа", url="https://t.me/+_Dcale1HD4RmYjM6")
        btn_5 = telebot.types.InlineKeyboardButton(text="Пригласить друга", callback_data="friends_adm")
        markup.add(btn_1, btn_2, btn_3, btn_4, btn_5, btn_6, btn_7, btn_8, btn_9, btn_10, btn_11, btn_12)
        bot.send_message(chat_id, f'''✨ Профиль Администратора
────────────────────────────
🫡 Ранг: {rank}
👤 Имя: {username}
🆔 ID: `{user_id}`
────────────────────────────
🤝 Ответов:  {otvet}
👥 Приглашенных друзей: {referals}
✅ Побед: {victory}
❌ Поражений: {defeat}
💰 Баланс: {points}


⬇️  Используй кнопки ниже, чтобы ввести промокод, 
играть или помогать боту.''', parse_mode="MARKDOWN", reply_markup=markup)
    else:
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn_1 = telebot.types.InlineKeyboardButton(text="Играть кубик", callback_data="cube")
        btn_2 = telebot.types.InlineKeyboardButton(text="Играть слоты", callback_data="slot")
        btn_3 = telebot.types.InlineKeyboardButton(text="Поддержка", callback_data="help")
        btn_4 = telebot.types.InlineKeyboardButton(text="Промокод", callback_data="promo")
        btn_5 = telebot.types.InlineKeyboardButton(text="Пригласить друга", callback_data="friends")
        markup.add(btn_1, btn_2, btn_3, btn_4, btn_5)
        bot.send_message(chat_id, f'''✨ Профиль
    ──────────────
    👤 Имя: {username}
    🆔 ID: `{user_id}`
    ──────────────
    👥 Приглашенных друзей: {referals}
    ✅ Побед: {victory}
    ❌ Поражений: {defeat}
    💰 Баланс {points}


    ⬇️  Используй кнопки ниже, чтобы ввести промокод, 
    играть или обратится в поддержку.''', parse_mode="MARKDOWN", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["cube_adm", "slot_adm", "help_adm", "promo_adm", "friends_adm", "ban", "adm+", "adm-", "promo+", "promo-","rep_adm"])
def confirmation(call):
    user = call.from_user
    chat_id = call.message.chat.id
    message = call.message

    if call.data == "cube_adm":
        confirmation_play_cube(user, chat_id)
    elif call.data == "slot_adm":
        game_slot(user, chat_id)
    elif call.data == "help_adm":
        help_soo(message)
    elif call.data == "promo_adm":
        promo2(user, chat_id)
    elif call.data == "friends_adm":
        send_ref_link(user, chat_id)
    elif call.data == "ban":
        pass
    elif call.data == "adm+":
        new_admin_command(user, chat_id)
    elif call.data == "adm-":
        new_kik_command(user, chat_id)
    elif call.data == "promo+":
        new_promo_command(user, chat_id)
    elif call.data == "promo-":
        kik_promo_command(user, chat_id)
    elif call.data == "rep_adm":
        answers_report(message)


@bot.callback_query_handler(func=lambda call: call.data in ["cube", "slot", "help", "promo", "friends"])
def confirmation2(call):
    message = call.message
    user = call.from_user
    chat_id = message.chat.id
    if call.data == "cube":
        confirmation_play_cube(user, chat_id)
    elif call.data == "slot":
        game_slot(user, chat_id)
    elif call.data == "help":
        help_soo(message)
    elif call.data == "promo":
        promo2(user, chat_id)
    elif call.data == "friends":
        send_ref_link(user, chat_id)


@bot.message_handler(commands=['shop'])
def shop_home(message):
    user = message.from_user
    chat_id = message.chat.id
    shop(user, chat_id)

def shop(user, chat_id):
    user_id = user.id
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()

    c.execute("SELECT points, donat FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    points, donat = result
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn_1 = telebot.types.InlineKeyboardButton(text="Вип  цена: 1000 монет/25 ДВ", callback_data="vip")
    btn_2 = telebot.types.InlineKeyboardButton(text="Вип+  цена: 1500 монет/35 ДВ", callback_data="vip_pluse")
    btn_3 = telebot.types.InlineKeyboardButton(text="1000 монет  цена: 25 ДВ", callback_data="money")
    btn_4 = telebot.types.InlineKeyboardButton(text="25 ДВ  цена: 1200", callback_data="donat_valute")
    btn_5 = telebot.types.InlineKeyboardButton(text="🔙 Меню", callback_data="back288")
    markup.add(btn_1, btn_2, btn_3, btn_4, btn_5)
    bot.send_message(chat_id, f'''🌟 Добро пожаловать в наш магазин! 🌟
Место, где качество и комфорт встречаются. Здесь вы найдете всё для вашего удовольствия по выгодным ценам.  

💎 Донат-валюта: {donat}
🪙 Монеты:  {points}

✨ Наслаждайтесь покупками и получайте максимум удовольствия! ✨

 ''', reply_markup = markup)

@bot.callback_query_handler(func=lambda call: call.data in ["vip", "vip_pluse", "money", "donat_valute", "back"])
def confirmation2(call):
    message = call.message
    user = call.from_user
    chat_id = message.chat.id
    if call.data == "vip":
        bot.send_message(chat_id, 'Ошибка!')
    elif call.data == "vip_pluse":
        bot.send_message(chat_id, 'Ошибка!')
    elif call.data == "money":
        покупка_монет(user, chat_id)
    elif call.data == "donat_valute":
        bot.send_message(chat_id, 'Ошибка!')
    elif call.data == "back":
        start_game(user, chat_id)

def покупка_монет(user, chat_id):
    user_id = user.id
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()

    c.execute("SELECT donat FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()  
    if result:
        donat = result[0]
    else:
        donat = 0
        
    if donat >= 25:
        c.execute(f'''
UPDATE users
SET donat = donat - 25
WHERE user_id = {user_id}
''')
        c.execute(f'''
UPDATE users
SET points = points + 1000
WHERE user_id = {user_id}
''')
    db.commit()
    db.close()
    bot.send_message(chat_id, '🎉 Всё готово! Теперь у тебя есть возможность приумножить свои средства и открыть новые горизонты. Вперёд к успеху и достижению новых целей! 🚀')
        

def minus_point(user, chat_id):
    user_id = user.id
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()

    c.execute(f'''
UPDATE users
SET balance = balance - 15
WHERE user_id = {user_id}
''')
    db.commit()
    db.close()

@bot.message_handler(commands=['admin+'])
def new_admin_command(user, chat_id):
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()

    c.execute("SELECT * FROM admin WHERE user_id=?", (user.id,))
    data = c.fetchone()

    if data is not None:
        c.execute("SELECT rank FROM admin WHERE user_id=?", (user.id,))
        rank = c.fetchone()
        rank_value = rank[0] if rank else None
        print(rank)
    else:
        rank = None
    if rank is not None:
        if rank_value == "Разработчик":
            # добавить меню с кнопками для постановки на страшего админа и на простого админа и кнопку назад
            adm = bot.send_message(chat_id, 'Введите айди человека, которого хотите назначить администратором:')
            bot.register_next_step_handler(adm, process_new_admin)
        elif rank_value == "Старший администратором":
            adm = bot.send_message(chat_id, 'Введите айди человека, которого хотите назначить администратором:')
            bot.register_next_step_handler(adm, process_new_admin)
            # добавить меню с кнопками для постановки на админа и кнопку назад
        else:
            bot.send_message(chat_id, 'Ошибка, не достаточно ранга для данного действия!')
            start_game(user, chat_id)
    else:
        bot.send_message(chat_id, 'Ошибка, вы не являетесь администратором')
        start_game(user, chat_id)

def process_new_admin(message):
    user = message.from_user
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()
    try:
        new_admin_id = int(message.text.strip())
        c.execute(
            "INSERT INTO admins (user_id, username, first_name, last_name, rank) VALUES (?, ?, ?, ?, ?)",
            (new_admin_id, user.username, user.first_name, user.last_name, "Администратор")
        )
        db.commit()
        bot.send_message(message.chat.id, 'Администратор добавлен!')
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите правильный числовой ID.')
        # Повторно вызываем
        msg = bot.send_message(message.chat.id, 'Введите айди человека, которого хотите назначить администратором:')
        bot.register_next_step_handler(msg, process_new_admin)
    except Exception as ex:
        bot.send_message(message.chat.id, f'Произошла ошибка: {ex}')

    print(admins_id)

@bot.message_handler(commands=['admin-'])
def new_kik_command(user, chat_id):
    if user.id in main_admins_id:
        adm = bot.send_message(chat_id, 'Введите айди человека, которого хотите уволить с поста администратор:')
        bot.register_next_step_handler(adm, process_kik_admin)
    else:
        if user.id in admins_id:
            bot.send_message(chat_id, 'Ошибка, у вас недостаточно ранга для этого действия!')
            start_game(user, chat_id)
        else:
            bot.send_message(chat_id, 'Ошибка, вы не являетесь администратором')
            start_game(user, chat_id)

def process_kik_admin(message):
    try:
        kik_admin_id = int(message.text.strip())
        admins_id.remove(kik_admin_id)
        bot.send_message(message.chat.id, 'Администратор уволен!')
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите правильный числовой ID.')
        # Повторно вызываем
        msg = bot.send_message(message.chat.id, 'Введите айди человека, которого хотите уволить с поста администратор:')
        bot.register_next_step_handler(msg, process_kik_admin)
    except Exception as ex:
        bot.send_message(message.chat.id, f'Произошла ошибка: {ex}')
    print(admins_id)

@bot.message_handler(commands=['promo+'])
def new_promo_command(user, chat_id):
    if user.id in main_admins_id:
        prm = bot.send_message(chat_id, 'Введите промокод, который вы хотите добавить:')
        bot.register_next_step_handler(prm, process_new_promo)
    else:
        if user.id in admins_id:
            bot.send_message(chat_id, 'Ошибка, у вас недостаточно ранга для этого действия!')
            start_game(user, chat_id)
        else:
            bot.send_message(chat_id, 'Ошибка, вы не являетесь администратором')
            start_game(user, chat_id)

def process_new_promo(message):
    try:
        new_promo = message.text.strip()
        promocod.append(new_promo)
        bot.send_message(message.chat.id, 'Промокод добавлен!')
    except Exception as ex:
        bot.send_message(message.chat.id, f'Произошла ошибка: {ex}')

    print(promocod)

@bot.message_handler(commands=['promo-'])
def kik_promo_command(user, chat_id):
    if user.id in main_admins_id:
        prm = bot.send_message(chat_id, 'Введите промокод, который вы хотите удалить:')
        bot.register_next_step_handler(prm, process_kik_promo)
    else:
        if user.id in admins_id:
            bot.send_message(chat_id, 'Ошибка, у вас недостаточно ранга для этого действия!')
            start_game(user, chat_id)
        else:
            bot.send_message(chat_id, 'Ошибка, вы не являетесь администратором')
            start_game(user, chat_id)

def process_kik_promo(message):
    try:
        kik_promo = message.text.strip()
        promocod.remove(kik_promo)
        bot.send_message(message.chat.id, 'Промокод удален!')
    except Exception as ex:
        bot.send_message(message.chat.id, f'Произошла ошибка: {ex}')
    print(promocod)

def help_soo(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_1 = telebot.types.InlineKeyboardButton(text="🔙 Меню", callback_data="back")
    btn_2 = telebot.types.InlineKeyboardButton(text="Поддержка", callback_data="report")
    markup.add(btn_1, btn_2)
    bot.send_message(message.chat.id, '''🌟 Добро пожаловать в наш бот! 🌟

Здесь вы найдете все необходимые команды и советы, чтобы максимально удобно и интересно пользоваться ботом.

──────────────────────────────
🔹 Основные команды:

🎲 /start /menu  

• Открывает ваше меню с возможностями.
• Для администраторов — доступен расширенный функционал.
🎰 /roulette  

• Играй в рулетку! Проверяй удачу и выигрывай призы!
• После запуска — наблюдай за результатом!
❗️ /report  

• Помогите улучшить бота! Напишите жалобы, идеи или отзывы — мы ценим ваше мнение.
📝 /promo  

• Активируй промокод для получения бонусов и подарков!
• Введите промокод после команды.
──────────────────────────────
🔸 Админ-команды:
(Доступны только для администраторов)

🛠 /admin+  

•Назначьте нового администратора.
📝 /promo+  

•Добавьте новый промокод для пользователей.
🔒 /ban  

• Блокируйте нарушителей и неподобающее поведение!
🔙 /rep  

• Ответьте на сообщения пользователей или управляйте обратной связью.
──────────────────────────────
💡 Советы по использованию:

• Используйте кнопки для быстрого взаимодействия — это удобно и быстро!
• Не забывайте вводить правильные ID при назначениях и ответах.
• Следите за новостями — мы постоянно обновляем функционал!
──────────────────────────────
📩 Обратная связь и предложения:  

👇Ниже — кнопки для обращения с просьбой или предложением по улучшению напрямую к администраторам.
Вы можете оставить отзыв или задать вопрос — наши администраторы обязательно помогут!  

[Обратиться с просьбой или предложением]  

🔙 Кнопка назад — возвращает вас к разделу админ-команд или основному меню.

─────────────────── ───────────
🎉 Желаем удачи и приятной игры!
Если есть идеи или вопросы — пишите в поддержку или в отзывы!''', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["back", "report"])
def confirmation2(call):
    user = call.from_user
    chat_id = call.message.chat.id
    if call.data == "back":
        start_game(user, chat_id)
    elif call.data == "report":
        report(call.message)

def start_game_from_user(user, chat_id):
    # Создаем фиктивное сообщение и вызываем start_game
    class FakeMessage:
        def __init__(self, user, chat_id):
            self.from_user = user
            self.chat = type('Chat', (), {'id': chat_id})()
    fake_msg = FakeMessage(user, chat_id)
    start_game(user, chat_id)


def confirmation_play_slot_still(user, chat_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_1 = telebot.types.InlineKeyboardButton(text="🔙 Меню", callback_data="back_slot_still")
    btn_2 = telebot.types.InlineKeyboardButton(text="🎰 Еще", callback_data="play_slot_still")
    markup.add(btn_1, btn_2)
    bot.send_message(chat_id, """🎉 Игра завершена! 🎉

Хочешь сыграть еще? Нажимай кнопку!""", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["back_slot_still", "play_slot_still"])
def confirmation4(call):
    user = call.from_user
    chat_id = call.message.chat.id
    if call.data == "back_slot_still":
        start_game(user, chat_id)
    elif call.data == "play_slot_still":
        game_slot(user, chat_id)

def confirmation_play_cube_still(user, chat_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_1 = telebot.types.InlineKeyboardButton(text="🔙 Меню", callback_data="back_cube_still")
    btn_2 = telebot.types.InlineKeyboardButton(text="🎲 Еще раз", callback_data="play_cube_still")
    markup.add(btn_1, btn_2)
    bot.send_message(chat_id, """🎉 Игра завершена! 🎉
Спасибо за участие!  

💰 Хотите попробовать снова?
🎰 Жмите "Крутить" и давайте удача улыбнется вам! 🍀  

🎉 Удачи и больших выигрышей! 🎉""", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["back_cube_still", "play_cube_still"])
def confirmation4(call):
    user = call.from_user
    chat_id = call.message.chat.id
    if call.data == "back_cube_still":
        start_game(user, chat_id)
    elif call.data == "play_cube_still":
        send_kubik(user, chat_id)

def confirmation_play_cube(user, chat_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_1 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="back_cube")
    btn_2 = telebot.types.InlineKeyboardButton(text="Играть", callback_data="play_cube")
    markup.add(btn_1, btn_2)
    bot.send_message(chat_id, """🎉 Добро пожаловать в увлекательную игру! 🎉

Стоимость участия — всего 15 монет.
Готовы испытать свою удачу?

✨ Условия игры:
🎲 Чтобы выиграть, нужно выбросить на кубике 6 очков! """, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["back_cube", "play_cube"])
def confirmation3(call):
    user = call.from_user
    chat_id = call.message.chat.id
    if call.data == "back_cube":
        start_game(user, chat_id)
    elif call.data == "play_cube":
        send_kubik(user, chat_id)

def send_kubik(user, chat_id):
    user_id = user.id
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()

    c.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()  
    if result:
        points = result[0]
    else:
        points = 0
    
    if points >= 15:
        try:
            c.execute(f'''
UPDATE users
SET points = points - ?
WHERE user_id = ? 
''', (15, user_id))
            db.commit()
            dice = bot.send_dice(chat_id, emoji='🎲')
            value = dice.dice.value

            bot.send_message(chat_id, 'Вам выпало...')
            time.sleep(1)  

            time.sleep(2)
            bot.send_message(chat_id, f'Число {value}!')
            if value == 6:
                bot.send_message(chat_id, "Поздравляю! Вы победили! Вам начисленно 50 монет!")
                c.execute(f'''
UPDATE users
SET points = points + ?
WHERE user_id = ? 
''', (50, user_id))
                c.execute(f'''
UPDATE users
SET victory = victory + ?
WHERE user_id = ? 
''', (1, user_id))
            
                db.commit()
                confirmation_play_cube_still(user, chat_id)
            else:
                bot.send_message(chat_id, "К сожелению вы проиграли, в следущий раз повезет.")
                c.execute(f'''
UPDATE users
SET defeat = defeat + ?
WHERE user_id = ? 
''', (1, user_id))
                db.commit()
                confirmation_play_cube_still(user, chat_id)
        except Exception as e:
            bot.send_message(chat_id, 'Произошла ошибка при броске кубика.')
            print(f"Ошибка: {e}")
    else:
        bot.send_message(chat_id, "Ошибка, недостаточно монет!")
        start_game(user, chat_id)
    db.close()

slots = ['🍒', '🍋', '🔔', '⭐', '💎']

@bot.message_handler(commands=['slot'])
def game_slot(user, chat_id):
    markup = telebot.types.InlineKeyboardMarkup()
    btn_1 = telebot.types.InlineKeyboardButton(text="🔙 Меню", callback_data="back4")
    btn_2 = telebot.types.InlineKeyboardButton(text='🎰 Крутить', callback_data='spin')
    markup.add(btn_1, btn_2)
    bot.send_message(chat_id, """🎉 Добро пожаловать в захватывающую игру на слотах! 🎉

Стоимость участия — всего 15 монет.
Готовы испытать свою удачу и сорвать джекпот?

✨ Условия игры:
🎰 Сделайте ставку и крутите барабаны!
🎯 Выигрыш зависит от совпадения символов на линиях!  

Удачи и больших выигрышей! 🍀 """, reply_markup=markup)

# Обработка нажатия кнопки
@bot.callback_query_handler(func=lambda call: call.data in ['back4', 'spin'])
def handle_spin(call):
    user = call.from_user
    chat_id = call.message.chat.id
      
    if call.data == 'spin':    
        slot_proces_game(user, chat_id)
    elif call.data == 'back4':
        start_game(user, chat_id)

def slot_proces_game(user, chat_id):
    user_id = user.id
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()

    c.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()  
    if result:
        points = result[0]
    else:
        points = 0

    if points >= 15:
        c.execute(f'''
    UPDATE users
    SET points = points - ?
    WHERE user_id = ? 
    ''', (15, user_id))
        db.commit()
        if random.random() < 0.33:
            symbol = random.choice(slots)
            result = [symbol] * 3
            won = True
        else:
                
            result = [random.choice(slots) for _ in range(3)]
                
            won = (result.count(result[0]) == len(result))
                
            if won:
                    
                result[2] = random.choice([s for s in slots if s != result[0]])

        result_text = ' | '.join(result)
        #confirmation_play_slot_still(user, chat_id)
        # Формируем сообщение
        if won:
            message_text = f"🎉 Вы выиграли! {result_text}"
            c.execute(f'''
UPDATE users
SET victory = victory + ?
WHERE user_id = ? 
''', (1, user_id))

            c.execute(f'''
UPDATE users
SET points = points + ?
WHERE user_id = ? 
''', (50, user_id))
            db.commit()
        else:
            message_text = f"Результат: {result_text}\nПопробуйте еще раз!"
            c.execute(f'''
UPDATE users
SET defeat = defeat + ?
WHERE user_id = ? 
''', (1, user_id))
            db.commit()
        #confirmation_play_slot_still(user, chat_id)
        # Отправляем результат и кнопку для повторного спина
        markup = telebot.types.InlineKeyboardMarkup()
        btn_1 = telebot.types.InlineKeyboardButton(text='🎰 Крутить снова', callback_data='spin')
        btn_2 = telebot.types.InlineKeyboardButton(text='🔙 Меню', callback_data='back5')
        markup.add(btn_2, btn_1)
        bot.send_message(chat_id, message_text, reply_markup=markup)
    else:
        bot.send_message(chat_id, '''🌟 Упс! 🌟
    У вас недостаточно монет, чтобы продолжить. 💰✨
    Пополните баланс и попробуйте снова — приключения ждут! 🚀🎮 ''')
        start_game(user, chat_id)

@bot.callback_query_handler(func=lambda call: call.data in ['back5','spin'])
def handle_spin(call):
    user = call.from_user
    chat_id = call.message.chat.id
    if call.data == 'back5':
        start_game(user, chat_id)
    elif call.data == 'spin':
        slot_proces_game(user, chat_id)

@bot.message_handler(commands=['/roulette'])
def roulette_game(user, chat_id):
    #user = message.from_user
    #chat_id = message.chat.id
    user_id = user.id
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()

    c.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()  
    if result:
        points = result[0]
    else:
        points = 0
        
    if points >= 15:
        c.execute(f'''
UPDATE users
SET points = points - ?
WHERE user_id = ? 
''', (15, user_id))
        db.commit()
        
        roulette_emoji = "🎰"
        msg = bot.send_message(chat_id, f"Начинается игра в рулетку! {roulette_emoji}\nКрутим...")
        result = random.randint(0, 1)
        if result == 1:
            bot.send_message(chat_id, "🎉 Поздравляем! Вы выиграли!")
            c.execute(f'''
UPDATE users
SET victory = victory + ?
WHERE user_id = ? 
''', (1, user_id))
            db.commit()
        else:
            bot.send_message(chat_id, "😞 Увы, вы проиграли. Попробуйте еще раз!")
            c.execute(f'''
UPDATE users
SET defeat = defeat + ?
WHERE user_id = ? 
''', (1, user_id))
            db.commit()
    else:
        bot.send_message(chat_id, "У вас не достаточно монет!")
        start_game(user, chat_id)
    db.close()

@bot.message_handler(commands=['report'])
def report(message):
    user = message.from_user
    chat_id = message.chat.id
    bot.send_message(message.chat.id,
                     '❗ПРЕДУПРЕЖДЕНИЕ:❗\nПри спаме вы навсегда потеряете доступ к боту на данном аккаунте!')
    bot.send_message(message.chat.id, 'Напишите вашу идею для проекта.')
    bot.register_next_step_handler(message, sms_global)

def sms_global(message):
    user = message.from_user
    chat_id = message.chat.id
    user_guess = message.text
    try:
        print(f'Пользователь {message.from_user.username}(ID:{message.from_user.id}) отправил СМС:', user_guess)
        group_chat_id = '-4979067893'
        full_message = f'Пользователь {message.from_user.username}(ID:`{message.from_user.id}`) отправил СМС: {user_guess}'
        bot.send_message(group_chat_id, full_message, parse_mode="MARKDOWN")
        bot.send_message(message.chat.id, 'Сообщение доставлено.')
        
    except Exception as ex:
        bot.send_message(message.chat.id, f'Ошибка доставки сообщения: {ex}')
    start_game(user, chat_id)

def answers_report(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_1 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="back1")
    btn_2 = telebot.types.InlineKeyboardButton(text="Отвечать", callback_data="report1")
    markup.add(btn_1, btn_2)
    bot.send_message(message.chat.id, '''📝 Репорты и Обратная Связь

Здравствуйте, уважаемые админы!

Для обработки репортов используйте группу: https://t.me/+zexHpKoMMt41NGUy. Там вы можете брать репорты и просматривать жалобы пользователей.

🔹 Как работать с репортами:
- Брать репорт нужно в группе по указанной ссылке.
- Отвечать пользователю необходимо через бота.
- После ответа — поставьте реакцию на репорт, чтобы другие админы не отвечали дважды.
- Для повторного ответа используйте команду /rep.

💡 Помните:
- Быстро реагируйте на обращения.
- Соблюдайте конфиденциальность и корректность.
- Обеспечивайте справедливое отношение к пользователям.

Спасибо за вашу работу! Если возникнут вопросы — обращайтесь к главным администраторам.

---

*Данный раздел предназначен только для админов. Не передавайте информацию третьим лицам.*''', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["back1", "report1"])
def confirmation3(call):
    user = call.from_user
    chat_id = call.message.chat.id
    if call.data == "back1":
        start_game(user, chat_id)
    elif call.data == "report1":
        user = call.from_user
        chat_id = call.message.chat.id
        otvet_id(user, chat_id)


@bot.message_handler(commands=['rep'])
def handle_rep_command(message):
    user = message.from_user
    chat_id = message.chat.id
    otvet_id(user, chat_id)

def otvet_id(user, chat_id):
    user_id = user.id
    # проверка прав администратора
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()

    c.execute("SELECT * FROM admin WHERE user_id=?", (user.id,))
    data = c.fetchone()

    if data is not None:
        c.execute("SELECT rank, otvet FROM admin WHERE user_id=?", (user_id,))
        result = c.fetchone()
        rank, otvet = result
        db.close()
    else:
        pass
    
    if data is not None:
        msg = bot.send_message(chat_id, 'Напишите айди пользователя:')
        bot.register_next_step_handler(msg, process_id, user, chat_id)
    else:
        bot.send_message(chat_id, 'Ошибка, вы не являетесь администратором')
        start_game(user, chat_id)
        
def process_id(message, user, chat_id):
    try:
        target_user_id = int(message.text.strip())
        msg = bot.send_message(chat_id, 'Напишите ваш ответ пользователю:')
        bot.register_next_step_handler(msg, send_answer, target_user_id, user, chat_id)
    except ValueError:
        bot.reply_to(message, 'Некорректный формат ID. Повторите попытку.')

def send_answer(message, target_user_id, user, chat_id):
    answer = message.text
    try:
        bot.send_message(target_user_id, answer)
        bot.send_message(chat_id, 'Сообщение доставлено.')
        # Обновление базы данных
        db = sqlite3.connect('BaseBot.db')
        c = db.cursor()
        c.execute(f'''
            UPDATE admin
            SET otvet = otvet + 1
            WHERE user_id = ?
        ''', (user.id,))
        db.commit()
        db.close()
    except Exception as ex:
        bot.send_message(chat_id, f'Ошибка доставки сообщения: {ex}')

@bot.message_handler(commands=['promo'])
def promo1(message):
    user = message.from_user
    chat_id = message.chat.id
    promo2(user, chat_id)


@bot.callback_query_handler(func=lambda call: call.data in ["back10"])
def confirmation7(call):
    user = call.from_user
    chat_id = call.message.chat.id
    start_game(user, chat_id)

def promo2(user, chat_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_1 = telebot.types.InlineKeyboardButton(text="🔙 Меню", callback_data="back10")
    markup.add(btn_1)
    pr = bot.send_message(chat_id, """🌟🎁 У вас уже есть промокод? 🎁🌟
Введите его ниже, чтобы активировать бонусы и насладиться приятными подарками! ✨🚀 """, reply_markup=markup)
    bot.register_next_step_handler(pr, process_promo)

def process_promo(message):
    user = message.from_user
    chat_id = message.chat.id
    if message.text.startswith("/"):
        return
    promo_code = message.text.strip()
    promo_list = ["start"]
    if promo_code in promo_list:
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn_1 = telebot.types.InlineKeyboardButton(text="🔙 Меню", callback_data="back11")
        btn_2 = telebot.types.InlineKeyboardButton(text="🔄 Ввести еще раз", callback_data="promo21")
        #btn_1 = telebot.types.InlineKeyboardButton(text="🔙 Меню" callback_data="back12")
        #btn_2 = telebot.types.InlineKeyboardButton(text="" callback_data="promo22")
        markup.add(btn_1, btn_2)
        bot.send_message(message.chat.id, """✨ Промокод успешно активирован! ✨
Хотите ввести еще один? """, reply_markup=markup)
    else:
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn_1 = telebot.types.InlineKeyboardButton(text="🔙 Меню", callback_data="back11")
        btn_2 = telebot.types.InlineKeyboardButton(text="🔄 Ввести еще раз", callback_data="promo21")
        markup.add(btn_1, btn_2)
        bot.send_message(message.chat.id, "❌ Промокод неверный или не найден. Попробуйте еще раз!❌", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["back11", "promo21"])
def confirmation8(call):
    user = call.from_user
    chat_id = call.message.chat.id
    if call.data == "back11":
        start_game(user, chat_id)
    elif call.data == "promo21":
        promo2(user, chat_id)

db.close()
bot.polling()
