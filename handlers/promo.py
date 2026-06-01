from db import *
import telebot

def promo_command(message, bot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_1 = telebot.types.InlineKeyboardButton(text="🔙 Меню", callback_data="back")
    markup.add(btn_1)
    msg = bot.send_message(chat_id, """🌟🎁 У вас уже есть промокод? 🎁🌟
Введите его ниже, чтобы активировать бонусы и насладиться приятными подарками! ✨🚀 """, reply_markup=markup)
    bot.register_next_step_handler(msg, process_promo_code, user_id, bot)

def process_promo_code(message, user_id, bot):
    code = message.text.strip().upper()
    valid, reward, error = is_promo_valid(code, user_id)
    if not valid:
        bot.send_message(message.chat.id, f"❌ {error}")
        return
    success, reward_amount = activate_promo(code, user_id)
    if success:
        bot.send_message(message.chat.id, f"✅ Промокод активирован! Вы получили {reward_amount} монет.")
    else:
        bot.send_message(message.chat.id, "❌ Ошибка при активации. Попробуйте позже.")


def add_promo_start(message, bot):
    # Проверка прав администратора (у тебя уже должна быть)
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Нет прав.")
        return
    msg = bot.send_message(message.chat.id, "Введите промокод, награду (в монетах), срок (ГГГГ-ММ-ДД, или 0 если бессрочно), лимит использований через пробел.\nПример: SUPER100 100 2025-12-31 5")
    bot.register_next_step_handler(msg, process_add_promo, bot)

def process_add_promo(message, bot):
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Неверный формат. Нужно: КОД НАГРАДА [СРОК] [ЛИМИТ]")
        return
    code = parts[0].upper()
    try:
        reward = int(parts[1])
    except:
        bot.reply_to(message, "❌ Награда должна быть числом.")
        return
    expires_at = None
    if len(parts) >= 3 and parts[2] != '0':
        expires_at = parts[2]
    uses_limit = 1
    if len(parts) >= 4:
        try:
            uses_limit = int(parts[3])
        except:
            pass
    success = add_promo_code(code, reward, expires_at, uses_limit)
    if success:
        bot.reply_to(message, f"✅ Промокод {code} добавлен.")
    else:
        bot.reply_to(message, "❌ Промокод уже существует.")


def remove_promo_start(message, bot):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Нет прав.")
        return
    msg = bot.send_message(message.chat.id, "Введите код промокода для удаления:")
    bot.register_next_step_handler(msg, process_remove_promo, bot)

def process_remove_promo(message, bot):
    code = message.text.strip().upper()
    if delete_promo_code(code):
        bot.reply_to(message, f"✅ Промокод {code} удалён.")
    else:
        bot.reply_to(message, "❌ Такой промокод не найден.")


def list_promos(message, bot):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Нет прав.")
        return
    promos = get_all_promocodes()
    if not promos:
        bot.reply_to(message, "Нет ни одного промокода.")
        return
    text = "📋 Список промокодов:\n"
    for code, reward, active, expires, limit, used in promos:
        status = "✅" if active else "❌"
        expires_str = expires if expires else "бессрочно"
        text += f"{status} {code}: +{reward} монет, использован {used}/{limit}, истекает: {expires_str}\n"
    bot.send_message(message.chat.id, text)