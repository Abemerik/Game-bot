import sqlite3
def referal_start(message, user, chat_id, bot):
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

def referal_link(bot, user, chat_id):
    bot_username = 'kazbotino_bot'
    ref_link = f"https://t.me/{bot_username}?start=ref_{user.id}"
    bot.send_message(chat_id, f"Ваша реферальная ссылка:\n{ref_link}")

