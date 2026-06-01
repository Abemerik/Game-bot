import telebot
import sqlite3
from handlers.start import *
from db import *

def new_admin(bot, user, chat_id):
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
            bot.register_next_step_handler(adm, process_new_admin, bot)
        elif rank_value == "Старший администратором":
            adm = bot.send_message(chat_id, 'Введите айди человека, которого хотите назначить администратором:')
            bot.register_next_step_handler(adm, process_new_admin, bot)
            # добавить меню с кнопками для постановки на админа и кнопку назад
        else:
            bot.send_message(chat_id, 'Ошибка, не достаточно ранга для данного действия!')
            start_game(bot, user, chat_id)
    else:
        bot.send_message(chat_id, 'Ошибка, вы не являетесь администратором')
        start_game(bot, user, chat_id)

def process_new_admin(message, bot):
    user = message.from_user
    chat_id = message.chat.id
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()
    try:
        new_admin_id = int(message.text.strip())
        result = db_request_newadmin(new_admin_id)
        if result:
            user_id, username, first_name, last_name = result
            c.execute(
            "INSERT INTO admin (user_id, username, first_name, last_name, rank) VALUES (?, ?, ?, ?, ?)",
            (new_admin_id, username, first_name,last_name, "Администратор")
        )
        else:
            bot.send_message(chat_id, "Пользователь с таким ID не найден")

        db.commit()
        bot.send_message(message.chat.id, 'Администратор добавлен!')
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите правильный числовой ID.')
        # Повторно вызываем
        msg = bot.send_message(message.chat.id, 'Введите айди человека, которого хотите назначить администратором:')
        bot.register_next_step_handler(msg, process_new_admin)
    except Exception as ex:
        bot.send_message(message.chat.id, f'Произошла ошибка: {ex}')

#----------NEW PROMO---------

#def new_promo(bot, user, chat_id):
#     if user.id in main_admins_id:
#        prm = bot.send_message(chat_id, 'Введите промокод, который вы хотите добавить:')
#        bot.register_next_step_handler(prm, process_new_promo, bot)
#    else:
#        if user.id in admins_id:
#            bot.send_message(chat_id, 'Ошибка, у вас недостаточно ранга для этого действия!')
#            start_game(user, chat_id)
#        else:
#            bot.send_message(chat_id, 'Ошибка, вы не являетесь администратором')
#            start_game(user, chat_id)

#def process_new_promo(message, bot):
#    try:
#        new_promo = message.text.strip()
#        promocod.append(new_promo)
#        bot.send_message(message.chat.id, 'Промокод добавлен!')
#    except Exception as ex:
#        bot.send_message(message.chat.id, f'Произошла ошибка: {ex}')

#    print(promocod)

def answers_report(message, bot):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_1 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="back")
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


def otvet_id(user, chat_id, bot):
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
        bot.register_next_step_handler(msg, process_id, user, chat_id, bot)
    else:
        bot.send_message(chat_id, 'Ошибка, вы не являетесь администратором')
        start_game(bot, user, chat_id)
        
def process_id(message, user, chat_id, bot):
    try:
        target_user_id = int(message.text.strip())
        msg = bot.send_message(chat_id, 'Напишите ваш ответ пользователю:')
        bot.register_next_step_handler(msg, send_answer, target_user_id, user, chat_id, bot)
    except ValueError:
        bot.reply_to(message, 'Некорректный формат ID. Повторите попытку.')

def send_answer(message, target_user_id, user, chat_id, bot):
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

#--------------------------------------
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


def new_promo_command(user, chat_id):
    new_promo(bot, user, chat_id)

#@bot.message_handler(commands=['promo-'])
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