import telebot
import sqlite3


def shop(bot, user, chat_id):
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
    btn_5 = telebot.types.InlineKeyboardButton(text="🔙 Меню", callback_data="back")
    markup.add(btn_1, btn_2, btn_3, btn_4, btn_5)
    bot.send_message(chat_id, f'''🌟 Добро пожаловать в наш магазин! 🌟
Место, где качество и комфорт встречаются. Здесь вы найдете всё для вашего удовольствия по выгодным ценам.  

💎 Донат-валюта: {donat}
🪙 Монеты:  {points}

✨ Наслаждайтесь покупками и получайте максимум удовольствия! ✨

 ''', reply_markup = markup)
