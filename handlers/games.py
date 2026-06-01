import telebot
import sqlite3
import time
import random
from handlers.start import *
from db import *

def confirmation_play_slot_still(bot, user, chat_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_1 = telebot.types.InlineKeyboardButton(text="🔙 Меню", callback_data="back")
    btn_2 = telebot.types.InlineKeyboardButton(text="🎰 Еще", callback_data="play_slot_still")
    markup.add(btn_1, btn_2)
    bot.send_message(chat_id, """🎉 Игра завершена! 🎉

Хочешь сыграть еще? Нажимай кнопку!""", reply_markup=markup)


def confirmation_play_cube_still(bot, user, chat_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_1 = telebot.types.InlineKeyboardButton(text="🔙 Меню", callback_data="back")
    btn_2 = telebot.types.InlineKeyboardButton(text="🎲 Еще раз", callback_data="play_cube_still")
    markup.add(btn_1, btn_2)
    bot.send_message(chat_id, """🎉 Игра завершена! 🎉
Спасибо за участие!  

💰 Хотите попробовать снова?
🎰 Жмите "Крутить" и давайте удача улыбнется вам! 🍀  

🎉 Удачи и больших выигрышей! 🎉""", reply_markup=markup)


def confirmation_play_cube(bot, user, chat_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_1 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="back")
    btn_2 = telebot.types.InlineKeyboardButton(text="Играть", callback_data="play_cube")
    markup.add(btn_1, btn_2)
    bot.send_message(chat_id, """🎉 Добро пожаловать в увлекательную игру! 🎉

Стоимость участия — всего 15 монет.
Готовы испытать свою удачу?

✨ Условия игры:
🎲 Чтобы выиграть, нужно выбросить на кубике 6 очков! """, reply_markup=markup)


def send_kubik(bot, user, chat_id):
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
            minus_point(user, chat_id)
            dice = bot.send_dice(chat_id, emoji='🎲')
            value = dice.dice.value

            bot.send_message(chat_id, 'Вам выпало...')
            time.sleep(1)  

            time.sleep(2)
            bot.send_message(chat_id, f'Число {value}!')
            if value == 6:
                bot.send_message(chat_id, "Поздравляю! Вы победили! Вам начисленно 50 монет!")
                pluse_point(user, chat_id)
                confirmation_play_cube_still(bot, user, chat_id)
            else:
                bot.send_message(chat_id, "К сожелению вы проиграли, в следущий раз повезет.")
                pluse_defeat(user, chat_id)
                confirmation_play_cube_still(bot, user, chat_id)
        except Exception as e:
            bot.send_message(chat_id, 'Произошла ошибка при броске кубика.')
            print(f"Ошибка: {e}")
    else:
        bot.send_message(chat_id, "Ошибка, недостаточно монет!")
        start_game(bot, user, chat_id)
    db.close()

slots = ['🍒', '🍋', '🔔', '⭐', '💎']


def game_slot(bot, user, chat_id):
    markup = telebot.types.InlineKeyboardMarkup()
    btn_1 = telebot.types.InlineKeyboardButton(text="🔙 Меню", callback_data="back")
    btn_2 = telebot.types.InlineKeyboardButton(text='🎰 Крутить', callback_data='spin')
    markup.add(btn_1, btn_2)
    bot.send_message(chat_id, """🎉 Добро пожаловать в захватывающую игру на слотах! 🎉

Стоимость участия — всего 15 монет.
Готовы испытать свою удачу и сорвать джекпот?

✨ Условия игры:
🎰 Сделайте ставку и крутите барабаны!
🎯 Выигрыш зависит от совпадения символов на линиях!  

Удачи и больших выигрышей! 🍀 """, reply_markup=markup)


def slot_proces_game(bot, user, chat_id):
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
        minus_point(user, chat_id)
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
            pluse_point(user, chat_id)
        else:
            message_text = f"Результат: {result_text}\nПопробуйте еще раз!"
            pluse_defeat(user, chat_id)
        confirmation_play_slot_still(bot, user, chat_id)
        # Отправляем результат и кнопку для повторного спина
        #markup = telebot.types.InlineKeyboardMarkup()
        #btn_1 = telebot.types.InlineKeyboardButton(text='🎰 Крутить снова', callback_data='spin')
        #btn_2 = telebot.types.InlineKeyboardButton(text='🔙 Меню', callback_data='back')
        #markup.add(btn_2, btn_1)
        #bot.send_message(chat_id, message_text, reply_markup=markup)
    else:
        bot.send_message(chat_id, '''🌟 Упс! 🌟
    У вас недостаточно монет, чтобы продолжить. 💰✨
    Пополните баланс и попробуйте снова — приключения ждут! 🚀🎮 ''')
        start_game(bot, user, chat_id)


#эта игра не используется
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