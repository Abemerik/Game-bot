import sqlite3
def create_table():
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

    c.execute('''CREATE TABLE IF NOT EXISTS promocodes (
        code TEXT PRIMARY KEY,
        reward_points INTEGER NOT NULL,
        active INTEGER DEFAULT 1,
        expires_at TIMESTAMP,
        uses_limit INTEGER DEFAULT 1,
        used_count INTEGER DEFAULT 0,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS promo_activations (
        user_id INTEGER,
        code TEXT,
        activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, code)
    )''')
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

def admins_plata():
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()
    # Получаем все user_id из таблицы admin
    c.execute("SELECT user_id FROM admin")
    user_ids = c.fetchall()
    # Обновляем points для каждого user_id
    for (user_id,) in user_ids:
        c.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (100, user_id))
    db.commit()
    db.close()

def  db_request_newadmin(new_admin_id):
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()

    c.execute("SELECT user_id, username, first_name, last_name FROM users WHERE user_id=?", (new_admin_id,))
    result = c.fetchone()
    db.close()
    return result


def minus_point(user, chat_id):
    user_id = user.id
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()

    c.execute(f'''
UPDATE users
SET points = points - ?
WHERE user_id = ?
''', (15, user_id))
    db.commit()
    db.close()

def pluse_point(user, chat_id): #еще добавляется победа
    user_id = user.id
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()

    c.execute('''
    UPDATE users
    SET points = points + ?
    WHERE user_id = ? 
    ''', (50, user_id))
    c.execute('''
    UPDATE users
    SET victory = victory + ?
    WHERE user_id = ? 
    ''', (1, user_id))
                
    db.commit()
    db.close()

def pluse_defeat(user, chat_id):
    user_id = user.id
    db = sqlite3.connect('BaseBot.db')
    c = db.cursor()

    c.execute('''
UPDATE users
SET defeat = defeat + ?
WHERE user_id = ? 
''', (1, user_id))
    db.commit()
    db.close()



def add_promo_code(code, reward_points, expires_at=None, uses_limit=1):
    conn = sqlite3.connect('BaseBot.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO promocodes (code, reward_points, expires_at, uses_limit)
                     VALUES (?, ?, ?, ?)''',
                  (code, reward_points, expires_at, uses_limit))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # код уже существует
    finally:
        conn.close()



def is_promo_valid(code, user_id):
    conn = sqlite3.connect('BaseBot.db')
    c = conn.cursor()
    c.execute('''SELECT reward_points, active, expires_at, uses_limit, used_count
                 FROM promocodes WHERE code = ?''', (code,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, None, "Такого промокода не существует."

    reward_points, active, expires_at, uses_limit, used_count = row

    if not active:
        conn.close()
        return False, None, "Промокод деактивирован."

    if expires_at:
        from datetime import datetime
        if datetime.now() > datetime.fromisoformat(expires_at):
            conn.close()
            return False, None, "Срок действия промокода истёк."

    # Исправленная проверка лимита
    if uses_limit and used_count >= uses_limit:
        conn.close()
        return False, None, "Промокод уже использован максимальное число раз."

    c.execute('SELECT 1 FROM promo_activations WHERE user_id = ? AND code = ?', (user_id, code))
    if c.fetchone():
        conn.close()
        return False, None, "Вы уже активировали этот промокод."

    conn.close()
    return True, reward_points, None

def activate_promo(code, user_id):
    conn = sqlite3.connect('BaseBot.db')
    c = conn.cursor()
    try:
        # Начинаем транзакцию
        c.execute('BEGIN')
        # Получаем награду
        c.execute('SELECT reward_points FROM promocodes WHERE code = ?', (code,))
        reward = c.fetchone()[0]
        # Начисляем пользователю
        c.execute('UPDATE users SET points = points + ? WHERE user_id = ?', (reward, user_id))
        # Увеличиваем счётчик использований
        c.execute('UPDATE promocodes SET used_count = used_count + 1 WHERE code = ?', (code,))
        # Записываем активацию
        c.execute('INSERT INTO promo_activations (user_id, code) VALUES (?, ?)', (user_id, code))
        conn.commit()
        return True, reward
    except Exception as e:
        conn.rollback()
        return False, None
    finally:
        conn.close()


def delete_promo_code(code):
    conn = sqlite3.connect('BaseBot.db')
    c = conn.cursor()
    c.execute('DELETE FROM promocodes WHERE code = ?', (code,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_all_promocodes():
    conn = sqlite3.connect('BaseBot.db')
    c = conn.cursor()
    c.execute('SELECT code, reward_points, active, expires_at, uses_limit, used_count FROM promocodes')
    rows = c.fetchall()
    conn.close()
    return rows


def is_admin(user_id):
    conn = sqlite3.connect('BaseBot.db')
    c = conn.cursor()
    c.execute("SELECT 1 FROM admin WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None