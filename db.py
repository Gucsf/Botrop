import aiosqlite
from config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                choice TEXT,
                stage TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def add_lead(user_id, username, first_name, choice, stage):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO leads (user_id, username, first_name, choice, stage) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, first_name, choice, stage),
        )
        await db.commit()


async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM leads") as cur:
            total = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM leads WHERE choice='accept'") as cur:
            accepted = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM leads WHERE choice='decline'") as cur:
            declined = (await cur.fetchone())[0]
    return total, accepted, declined
