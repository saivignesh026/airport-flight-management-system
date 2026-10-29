"""Database helpers; each operation owns and closes its connection."""
import os
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def is_restricted_delete_error(error):
        """Return True when MySQL blocks a delete because child rows exist."""
        return (
                getattr(error, 'errno', None) == 1451
                or getattr(error, 'sqlstate', None) == '23000'
        )

def get_db_connection():
    return mysql.connector.connect(
        user=os.getenv('DB_USER'),
        host=os.getenv('DB_HOST', 'localhost'),
        password=os.getenv('DB_PASSWORD'),
        port=int(os.getenv('DB_PORT') or '3306'),
        database=os.getenv('DB_NAME'),
        time_zone='+05:30',
        connection_timeout=10,
    )


def _drain_results(cur):
    # CALL may return multiple result sets, including a final empty status set.
    # Consume them before committing or closing to avoid unread-result errors.
    while True:
        if cur.with_rows:
            cur.fetchall()
        if not cur.nextset():
            break


@contextmanager
def _cursor(dictionary=True):
    conn = get_db_connection()
    cur = None
    try:
        cur = conn.cursor(dictionary=dictionary, buffered=True)
        yield conn, cur
    finally:
        try:
            if cur is not None:
                cur.close()
        finally:
            conn.close()


def fetch_all(sql, params=()):
    with _cursor() as (_, cur):
        cur.execute(sql, params)
        rows = cur.fetchall()
        _drain_results(cur)
        return rows


def fetch_one(sql, params=()):
    with _cursor() as (_, cur):
        cur.execute(sql, params)
        row = cur.fetchone()
        _drain_results(cur)
        return row


def execute(sql, params=()):
    with _cursor(dictionary=False) as (conn, cur):
        try:
            cur.execute(sql, params)
            lastrowid = cur.lastrowid
            _drain_results(cur)
            conn.commit()
            return lastrowid
        except Exception:
            conn.rollback()
            raise


@contextmanager
def transaction():
    with _cursor() as (conn, cur):
        try:
            yield cur
            _drain_results(cur)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
