import telebot
from handlers.start import *


def report_user(message, bot):
    user = message.from_user
    chat_id = message.chat.id
    bot.send_message(message.chat.id,
                     '❗ПРЕДУПРЕЖДЕНИЕ:❗\nПри спаме вы навсегда потеряете доступ к боту на данном аккаунте!')
    bot.send_message(message.chat.id, 'Напишите вашу идею для проекта.')
    bot.register_next_step_handler(message, sms_global, bot)

def sms_global(message, bot):
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
    start_game(bot, user, chat_id)