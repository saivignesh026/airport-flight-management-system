import mysql.connector
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()


def is_restricted_delete_error(error):
        """Return True when MySQL blocks a delete because child rows exist."""
        return (
                getattr(error, 'errno', None) == 1451
                or getattr(error, 'sqlstate', None) == '23000'
        )

def get_db_connection():
        return mysql.connector.connect(
                user=os.getenv("DB_USER"),
                host=os.getenv("DB_HOST"),
                password=os.getenv("DB_PASSWORD"),
                port=int(os.getenv("DB_PORT")),
                database=os.getenv("DB_NAME"),
                time_zone="+05:30"
        )

def fetch_all(sql,params=()):
        conn=get_db_connection()
        cur=conn.cursor(dictionary=True)
        try:
                cur.execute(sql,params)
                return cur.fetchall()
        finally:
                cur.close()
                conn.close()

def fetch_one(sql,params=()):
        conn=get_db_connection()
        cur=conn.cursor(dictionary=True)
        try:
                cur.execute(sql,params)
                return cur.fetchone()
        finally:
                cur.close()
                conn.close()

def execute(sql,params=()):
        conn=get_db_connection()
        cur=conn.cursor()
        try:
                cur.execute(sql,params)
                conn.commit()
                return cur.lastrowid
        except Exception:
                conn.rollback()
                raise
        finally:
                cur.close()
                conn.close()


@contextmanager
def transaction():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
