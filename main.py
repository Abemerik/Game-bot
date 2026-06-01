import telebot
import time
import random
import logging
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from decouple import config
from db import *
from handlers.referal import *
from handlers.start import *
from handlers.shop import *
from handlers.user import *
from handlers.admin import *
from handlers.games import *
from handlers.reports import *
from handlers.promo import *

db = sqlite3.connect('BaseBot.db')
c = db.cursor()

create_table()

token = config("TOKEN")

bot = telebot.TeleBot(token)
admin_chat_id = config('ADMIN_CHAT_ID', default=0, cast=int)

bot_id = None
try:
    bot_id = bot.get_me().id
except:
    pass

#admins_plata()


#scheduler = BackgroundScheduler()
#scheduler.add_job(admins_plata, 'cron', hour=12, minute=10)
#scheduler.start()

admins_plata()

@bot.message_handler(commands=['ref'])
def process_ref_link(message):
    user = message.from_user
    chat_id = message.chat.id
    send_ref_link(user, chat_id)

def send_ref_link(user, chat_id):
    get_or_create_user(user)
    referal_link(bot, user, chat_id)

@bot.message_handler(commands=['start', 'menu'])
def process_handle_start(message):
    user = message.from_user
    chat_id = message.chat.id

    # Создаём пользователя, если его ещё нет
    get_or_create_user(user)
    # Проверка перехода по реферальной ссылке
    referal_start(message, user, chat_id, bot)
    # вызываем основную функцию стартовой логики
    start_game(bot, user, chat_id)

#@bot.message_handler(commands=['start', 'menu'])
def start_command(message):
    user = message.from_user
    chat_id = message.chat.id
    start_game(bot, user, chat_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user = call.from_user
    chat_id = call.message.chat.id
    message = call.message

    if call.data == "ban":
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
        answers_report(message, bot)
    elif call.data == "cube":
        confirmation_play_cube(bot, user, chat_id)
    elif call.data == "slot":
        game_slot(bot, user, chat_id)
        print("game slot open")
    elif call.data == "help":
        help_soo(message, bot)
    elif call.data == "promo":
        promo_command(message, bot)
    elif call.data == "friends":
        send_ref_link(user, chat_id)
    elif call.data == "back":
        start_game(bot, user, chat_id)
    elif call.data == "report":
        report(call.message)
    elif call.data == "play_cube":
        send_kubik(bot, user, chat_id)
    elif call.data == 'spin':
        slot_proces_game(bot, user, chat_id)
        print("slot_proces_game open")
    elif call.data == "report1":
        otvet_id(user, chat_id, bot)
    elif call.data == "play_cube_still":
        send_kubik(bot, user, chat_id)

@bot.message_handler(commands=['shop'])
def shop_home(message):
    user = message.from_user
    chat_id = message.chat.id
    shop(bot, user, chat_id)

@bot.message_handler(commands=['newadmin'])
def new_admin_command(message):
    user = message.from_user
    chat_id = message.chat.id
    new_admin(bot, user, chat_id)

@bot.message_handler(commands=['admin-'])


@bot.message_handler(commands=['promo+'])

@bot.message_handler(commands=['cube'])
def game_cube(message):
    user = message.from_user
    chat_id = message.chat.id
    confirmation_play_cube(bot, user, chat_id)

@bot.message_handler(commands=['roulette'])


@bot.message_handler(commands=['report'])
def report(message):
   report_user(message, bot)

@bot.message_handler(commands=['rep'])
def rep_admin(message):
    answers_report(message, bot)

@bot.message_handler(commands=['promo'])
def promo_commans_main(message):
    promo_command(message, bot)

@bot.message_handler(commands=['promopluse'])
def add_promo_main(message):
    add_promo_start(message, bot)


@bot.message_handler(commands=['promominuse'])
def remove_ptomo_main(message):
    remove_promo_start(message, bot)


@bot.message_handler(commands=['promolist'])
def promolist_main(message):
    list_promos(message, bot)

db.close()

if __name__ == '__main__':
    bot.polling(none_stop=True)

