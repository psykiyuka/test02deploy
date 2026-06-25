import os
import logging
from contextlib import contextmanager

from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor

logger = logging.getLogger("shop")

_pool: ThreadedConnectionPool = None

# 从环境变量读取数据库连接字符串，默认值使用 Docker 内部服务名
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:1234@postgres:5432/agent")


def init_pool():
    global _pool
    _pool = ThreadedConnectionPool(minconn=5, maxconn=50, dsn=DATABASE_URL)

    conn = _pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO shop")
    finally:
        _pool.putconn(conn)

    logger.info("数据库连接池初始化完成 | min=5 max=50")


def close_pool():
    global _pool
    if _pool:
        _pool.closeall()
        logger.info("数据库连接池已关闭")


def get_connection():
    conn = _pool.getconn()
    conn.autocommit = True
    return conn


def release_connection(conn):
    if conn:
        conn.autocommit = True
        _pool.putconn(conn)


@contextmanager
def get_cursor():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)