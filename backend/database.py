import sqlite3
import json

DB_NAME = "app.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            old_name TEXT,
            new_name TEXT,
            score TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


def save_request(customer_id, old_name, new_name, score, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO requests (customer_id, old_name, new_name, score, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        customer_id,
        old_name,
        new_name,
        json.dumps(score),
        status
    ))

    request_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return request_id


# ✅ UPDATED: include ESCALATED also
def get_pending_requests():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM requests
        WHERE status IN ('AI_VERIFIED_PENDING_HUMAN', 'ESCALATED')
    """)

    rows = cursor.fetchall()
    conn.close()

    return format_rows(rows)


def get_processed_requests():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM requests
        WHERE status = 'APPROVED' OR status = 'REJECTED'
    """)

    rows = cursor.fetchall()
    conn.close()

    return format_rows(rows)


def update_status(request_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE requests
        SET status = ?
        WHERE id = ?
    """, (status, request_id))

    conn.commit()
    conn.close()


def format_rows(rows):
    result = []

    for row in rows:
        result.append({
            "id": row[0],
            "customer_id": row[1],
            "old_name": row[2],
            "new_name": row[3],
            "score": json.loads(row[4]),
            "status": row[5]
        })

    return result