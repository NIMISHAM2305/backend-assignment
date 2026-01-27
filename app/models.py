import sqlite3
from app.config import settings
from datetime import datetime


def get_connection():
    # DATABASE_URL example: sqlite:///./app.db
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            from_msisdn TEXT NOT NULL,
            to_msisdn   TEXT NOT NULL,
            ts          TEXT NOT NULL,
            text        TEXT,
            created_at  TEXT NOT NULL
        );
        """
    )

    conn.commit()
    conn.close()

def check_db():
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return True
    except Exception:
        return False


def insert_message(message):
    """
    Returns:
      - "created" if inserted
      - "duplicate" if message_id already exists
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO messages (
                message_id,
                from_msisdn,
                to_msisdn,
                ts,
                text,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                message.message_id,
                message.from_msisdn,
                message.to_msisdn,
                message.ts,
                message.text,
                datetime.utcnow().isoformat() + "Z",
            ),
        )

        conn.commit()
        conn.close()
        return "created"

    except sqlite3.IntegrityError:
        # message_id already exists (PRIMARY KEY)
        return "duplicate"

def fetch_messages(
    limit: int,
    offset: int,
    from_msisdn: str | None = None,
    since: str | None = None,
    q: str | None = None,
):
    conn = get_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if from_msisdn:
        conditions.append("from_msisdn = ?")
        params.append(from_msisdn)

    if since:
        conditions.append("ts >= ?")
        params.append(since)

    if q:
        conditions.append("text LIKE ?")
        params.append(f"%{q}%")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    # total count (without limit/offset)
    cursor.execute(
        f"SELECT COUNT(*) FROM messages {where_clause}",
        params,
    )
    total = cursor.fetchone()[0]

    # actual data
    cursor.execute(
        f"""
        SELECT message_id, from_msisdn, to_msisdn, ts, text
        FROM messages
        {where_clause}
        ORDER BY ts ASC, message_id ASC
        LIMIT ? OFFSET ?
        """,
        params + [limit, offset],
    )

    rows = cursor.fetchall()
    conn.close()

    data = [
        {
            "message_id": row["message_id"],
            "from": row["from_msisdn"],
            "to": row["to_msisdn"],
            "ts": row["ts"],
            "text": row["text"],
        }
        for row in rows
    ]

    return data, total

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT from_msisdn) FROM messages")
    senders_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT from_msisdn, COUNT(*) as count
        FROM messages
        GROUP BY from_msisdn
        ORDER BY count DESC
        LIMIT 10
        """
    )
    messages_per_sender = [
        {"from": row["from_msisdn"], "count": row["count"]}
        for row in cursor.fetchall()
    ]

    cursor.execute("SELECT MIN(ts), MAX(ts) FROM messages")
    row = cursor.fetchone()
    first_message_ts = row[0]
    last_message_ts = row[1]

    conn.close()

    return {
        "total_messages": total_messages,
        "senders_count": senders_count,
        "messages_per_sender": messages_per_sender,
        "first_message_ts": first_message_ts,
        "last_message_ts": last_message_ts,
    }
