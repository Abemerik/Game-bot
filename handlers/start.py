import telebot
from db import *

def start_game(bot, user, chat_id):
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
        btn_1 = telebot.types.InlineKeyboardButton(text="Играть кубик", callback_data="cube")
        btn_2 = telebot.types.InlineKeyboardButton(text="Играть слоты", callback_data="slot")
        btn_3 = telebot.types.InlineKeyboardButton(text="Поддержка", callback_data="help")
        btn_4 = telebot.types.InlineKeyboardButton(text="Промокод", callback_data="promo")
        btn_6 = telebot.types.InlineKeyboardButton(text="Репорты", callback_data="rep_adm")
        btn_7 = telebot.types.InlineKeyboardButton(text="Группа", url="https://t.me/+_Dcale1HD4RmYjM6")
        btn_5 = telebot.types.InlineKeyboardButton(text="Пригласить друга", callback_data="friends")
        markup.add(btn_1, btn_2, btn_3, btn_4, btn_5, btn_6, btn_7)
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
