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
    image_size INTEGER);''')
    cur.execute('''CREATE TABLE IF NOT EXISTS payments(
    id INTEGER PRIMARY KEY,
    payer_id INTEGER,
    date INTEGER,
    status TEXT);''')
    conn.commit()
def create_user(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users WHERE user_id = {user_id};''')
    if cur.fetchall():
        return
    cur.execute(f'''INSERT INTO users(user_id, refs, daily_balance, current_balance, subscription_data, language, image_size) VALUES({user_id}, 0, 4000, 4000, 0, 'en', 256)''')
    conn.commit()
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
def new_balance():
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
def create_payment(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''INSERT INTO payments (payer_id , data, status) VALUES ({user_id}, {time.time()}, 'created');''')
    conn.commit()
def change_payment_status(user_id, status):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute(f'''UPDATE payments SET status = '{status}' WHERE user_id = {user_id};''')
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
