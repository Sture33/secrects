import time

import aiosqlite

DB_NAME = "database.db"


async def init_db():
    conn = await aiosqlite.connect(DB_NAME)
    cursor = await conn.cursor()
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            user_first_name TEXT,
            user_last_name TEXT,
            username TEXT,
            last_question_at INTEGER )
        """)
    await cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions(
                id INTEGER PRIMARY KEY,
                question_id INTEGER,
                question_owner_id INTEGER,
                FOREIGN KEY (question_owner_id) REFERENCES users(user_id)
            )
    """)
    await cursor.execute("""
    CREATE TABLE IF NOT EXISTS anonymous_answers(
        id INTEGER PRIMARY KEY,
        question_id INTEGER,
        answer_owner_id INTEGER,
        FOREIGN KEY (question_id) REFERENCES questions(question_id),
        FOREIGN KEY (answer_owner_id) REFERENCES users(user_id))
    """)

    await conn.commit()
    await conn.close()


async def create_new_user(user_id, user_first_name, user_last_name, username):
    conn = await aiosqlite.connect(DB_NAME)
    cursor = await conn.cursor()
    try:
        await cursor.execute("INSERT INTO users (user_id, user_first_name, user_last_name, username) VALUES (?,?,?,?)",
                             (user_id, user_first_name, user_last_name, username))
        await conn.commit()
    finally:
        await conn.close()
    return user_id


async def get_all_users():
    conn = await aiosqlite.connect(DB_NAME)
    cursor = await conn.cursor()
    await cursor.execute("SELECT user_id, username FROM users")
    users = await cursor.fetchall()
    await conn.close()
    return users


async def check_user(userid):
    conn = await aiosqlite.connect(DB_NAME)
    cursor = await conn.cursor()
    await cursor.execute("SELECT * FROM users WHERE user_id = ?", (int(userid),))
    user = await cursor.fetchone()
    await conn.close()
    if user:
        return True
    return False


async def can_ask_question(user_id):
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.execute(
                "SELECT last_question_at FROM users WHERE user_id = ?",
                (user_id,)
        ) as cursor:
            row = await cursor.fetchone()

        current_time = int(time.time())

        if row is None:
            return False

        last_time = row[0]

        if last_time is None:
            return True

        if current_time - last_time >= 300:
            return True
        else:
            return False


async def update_question_time(user_id):
    async with aiosqlite.connect(DB_NAME) as conn:
        await conn.execute(
            "UPDATE users SET last_question_at = ? WHERE user_id = ?",
            (int(time.time()), user_id)
        )
        await conn.commit()


async def get_question_time(user_id):
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.execute(
                "SELECT last_question_at FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
    if row:
        return row[0]
    return None

async def create_new_question(user_id,question_id):
    async with aiosqlite.connect(DB_NAME) as conn:
        await conn.execute(
            'INSERT INTO questions (question_id, question_owner_id) VALUES (?,?)',
            (question_id, user_id)
        )
        await conn.commit()

async def create_new_anonymous_answer(user_id,question_id):
    async with aiosqlite.connect(DB_NAME) as conn:
        await conn.execute(
            'INSERT INTO anonymous_answers (question_id, answer_owner_id) VALUES (?,?)',
            (question_id, user_id)
        )
        await conn.commit()

async def get_question_owner(question_id):
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.execute(
            'SELECT question_owner_id FROM questions WHERE question_id = ?',(question_id,)
        ) as cursor:
            row = await cursor.fetchone()
        if row:
            return row[0]
        else:
            return None
