
import sqlite3
from villagers import VILLAGERS

DB_NAME = "tiny_town.db"


def connect():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def initialize():
    with connect() as db:

        # SETTINGS TABLE
        db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # VILLAGERS TABLE
        db.execute("""
            CREATE TABLE IF NOT EXISTS villagers (
                name TEXT PRIMARY KEY,
                mood TEXT,
                energy INTEGER,
                personality TEXT,
                secret TEXT,
                backstory TEXT,
                goal TEXT
            )
        """)

        # MEMORIES TABLE
        db.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                villager TEXT,
                memory TEXT,
                day INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # RELATIONSHIPS TABLE
        db.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                person1 TEXT,
                person2 TEXT,
                score INTEGER DEFAULT 0,
                PRIMARY KEY(person1, person2)
            )
        """)

        # EVENTS TABLE
        db.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day INTEGER,
                category TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # INITIALIZE DAY
        result = db.execute(
            "SELECT value FROM settings WHERE key='day'"
        ).fetchone()

        if result is None:
            db.execute(
                "INSERT INTO settings (key, value) VALUES ('day', '1')"
            )

        # INITIALIZE VILLAGERS
        for v in VILLAGERS:
            db.execute("""
                INSERT OR IGNORE INTO villagers
                (name, mood, energy, personality, secret, backstory, goal)
                VALUES (?, 'Happy', 100, ?, ?, ?, ?)
            """, (
                v["name"],
                v["personality"],
                v["secret"],
                v["backstory"],
                v["goal"]
            ))

        # INITIALIZE RELATIONSHIPS
        for i, first in enumerate(VILLAGERS):
            for second in VILLAGERS[i + 1:]:

                db.execute("""
                    INSERT OR IGNORE INTO relationships
                    (person1, person2, score)
                    VALUES (?, ?, 0)
                """, (
                    first["name"],
                    second["name"]
                ))


# GET CURRENT DAY
def get_day():
    with connect() as db:
        result = db.execute(
            "SELECT value FROM settings WHERE key='day'"
        ).fetchone()

        return int(result[0])


# SET CURRENT DAY
def set_day(day):
    with connect() as db:
        db.execute(
            "UPDATE settings SET value=? WHERE key='day'",
            (str(day),)
        )


# GET ALL VILLAGERS
def get_villagers():
    with connect() as db:
        rows = db.execute("""
            SELECT name, mood, energy
            FROM villagers
        """).fetchall()

    return {
        name: {
            "mood": mood,
            "energy": energy
        }
        for name, mood, energy in rows
    }


# UPDATE VILLAGER
def update_villager(name, mood=None, energy=None):
    with connect() as db:

        if mood is not None:
            db.execute("""
                UPDATE villagers
                SET mood=?
                WHERE name=?
            """, (mood, name))

        if energy is not None:
            db.execute("""
                UPDATE villagers
                SET energy=?
                WHERE name=?
            """, (energy, name))


# ADD MEMORY
def add_memory(name, memory, day):
    with connect() as db:
        db.execute("""
            INSERT INTO memories (villager, memory, day)
            VALUES (?, ?, ?)
        """, (name, memory, day))


# GET MEMORIES
def get_memories(name, limit=8):
    with connect() as db:
        rows = db.execute("""
            SELECT memory, day
            FROM memories
            WHERE villager=?
            ORDER BY id DESC
            LIMIT ?
        """, (name, limit)).fetchall()

    # Return oldest to newest among retrieved memories
    return rows[::-1]


# ADD EVENT
def add_event(day, category, description):
    with connect() as db:
        db.execute("""
            INSERT INTO events (day, category, description)
            VALUES (?, ?, ?)
        """, (day, category, description))


# GET EVENTS
def get_events(limit=30):
    with connect() as db:
        return db.execute("""
            SELECT day, category, description
            FROM events
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()


# CHANGE RELATIONSHIP
def change_relationship(first, second, amount):
    if first == second:
        return

    with connect() as db:
        db.execute("""
            UPDATE relationships
            SET score = MAX(-100, MIN(100, score + ?))
            WHERE (person1=? AND person2=?)
               OR (person1=? AND person2=?)
        """, (
            amount,
            first, second,
            second, first
        ))


# GET ALL RELATIONSHIPS
def get_relationships():
    with connect() as db:
        return db.execute("""
            SELECT person1, person2, score
            FROM relationships
            ORDER BY score DESC
        """).fetchall()


# GET TWO VILLAGERS' RELATIONSHIP
def relationship_between(first, second):
    with connect() as db:

        result = db.execute("""
            SELECT score
            FROM relationships
            WHERE person1=? AND person2=?
        """, (first, second)).fetchone()

        if result is None:
            result = db.execute("""
                SELECT score
                FROM relationships
                WHERE person1=? AND person2=?
            """, (second, first)).fetchone()

    return result[0] if result else 0
