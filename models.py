import sqlite3

def get_connection():
    return sqlite3.connect('shorturl.db', detect_types=sqlite3.PARSE_DECLTYPES)

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_url TEXT NOT NULL,
        shortcode TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP
    )''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS click_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url_id INTEGER,
        timestamp TIMESTAMP,
        referrer TEXT,
        location TEXT,
        FOREIGN KEY (url_id) REFERENCES urls(id)
    )''')
    conn.commit()
    conn.close()
