import sqlite3
import time


def start():
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER UNIQUE,
    refs INTEGER,
    daily_balance INTEGER,
    current_balance INTEGER,
    subscription_data INTEGER,
    language TEXT,
    image_size INTEGER,
    inviter_id INTEGER,
    context INTEGER,
    previous_prompt TEXT);''')
    cur.execute('''CREATE TABLE IF NOT EXISTS payments(
    id INTEGER PRIMARY KEY,
    payer_id INTEGER,
    date INTEGER,
    status TEXT,
    bill_id TEXT);''')
    conn.commit()
def create_user(user_id, inviter_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users WHERE user_id = {user_id};''')
    if cur.fetchall():
        return
    cur.execute(f'''INSERT INTO users(user_id, refs, daily_balance, current_balance, subscription_data, language, image_size, inviter_id) VALUES({user_id}, 0, 4000, 4000, 0, 'en', 256, {inviter_id})''')
    if inviter_id:
        add_ref(inviter_id)
    conn.commit()
def add_to_prompt(user_id, text):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users WHERE user_id = {user_id};''')
    data = cur.fetchall()[0][9]
    data = data + '\n' + text
    cur.execute(f'''UPDATE users SET previous_prompt = {data};''')
    conn.commit()
def get_prompt(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users WHERE user_id = {user_id};''')
    data = cur.fetchall()[0][9]
    return data
def break_prompt(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''UPDATE users SET previous_prompt = '' WHERE user_id = {user_id};''')
    conn.commit()
def check_existing_payments(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM payments WHERE payer_id = {user_id} AND status = 'active';''')
    data = cur.fetchall()
    if data:
        return True
    else:
        return False
def restart_payments(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''UPDATE payments SET status = 'inactive' WHERE payer_id = {user_id} AND status = 'active';''')
    conn.commit()
def get_context_status(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users WHERE user_id = {user_id};''')
    data =cur.fetchall()[0][8]
    if data == 1:
        return True
    else:
        return False
def change_context_status(user_id, new_status):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''UPDATE users SET context = {new_status} WHERE user_id = {user_id};''')
    conn.commit()
    break_prompt(user_id)
def add_ref(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users WHERE user_id = {user_id};''')
    data = cur.fetchall()
    if data:
        data = data[0][1]
    else:
        return
    cur.execute(f'''UPDATE users SET ref = {data+1} WHERE user_id = {user_id};''')
    cur.execute(f'''UPDATE users SET daily_balance = {4000 + (data+1)* 100};''')
    conn.commit()
def spend_balance(user_id, amount):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users WHERE user_id = {user_id};''')
    data = cur.fetchall()[0][3]
    if amount <= data:
        cur.execute(f'''UPDATE users SET current_balance = {amount-data} WHERE user_id = {user_id};''')
        return True
    else:
        return False
async def new_balance():
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users;''')
    data = cur.fetchall()
    for i in data:
        user_id = i[0]
        daily_balance = i[2]
        cur.execute(f'''UPDATE users SET current_balance = {daily_balance} WHERE user_id = {user_id};''')
    conn.commit()
def check_subscription(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users WHERE user_id = {user_id};''')
    data = cur.fetchall()[0][4]
    if time.time() - data <= 30 * 24 * 60 *60:
        return True
    else:
        return False
def add_subscription(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''UPDATE users SET subscription_data = {time.time()} WHERE user_id = {user_id};''')
    conn.commit()
def create_payment(user_id, bill_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''UPDATE payments SET status = 'inactive' WHERE payer_id = {user_id} AND {int(time.time())}-date > 900;''')
    cur.execute(f'''INSERT INTO payments (payer_id , date, status, bill_id) VALUES ({user_id}, {int(time.time())}, 'active', '{bill_id}');''')
    conn.commit()
def change_payment_status(user_id,bill_id, status):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''UPDATE payments SET status = '{status}' WHERE payer_id = {user_id} AND bill_id = '{bill_id}';''')
    conn.commit()
def set_language(user_id, language):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''UPDATE users SET language = '{language}' WHERE user_id = {user_id};''')
    conn.commit()
def get_language(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users WHERE user_id = {user_id};''')
    data = cur.fetchall()[0][5]
    return data
def get_balance(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users WHERE user_id = {user_id};''')
    data = cur.fetchall()[0][3]
    return data
def get_daily_balance(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users WHERE user_id = {user_id};''')
    data = cur.fetchall()[0][2]
    return data
def get_refs(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users WHERE user_id = {user_id};''')
    data = cur.fetchall()[0][1]
    return data
def get_image_size(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users WHERE user_id = {user_id};''')
    data = cur.fetchall()[0][6]
    return data
def change_image_size(user_id, size):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''UPDATE users SET image_size = {size} WHERE user_id = {user_id};''')
    conn.commit()
