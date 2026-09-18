import inspect
import os
import uuid
import pytest
import logging

from firebird.driver import connect, create_database


@pytest.fixture
def fb_db(tmp_path):
    """
    Создаём временную БД Firebird (setup) и удаляем файл (teardown).
    """
    log = logging.getLogger(__name__)
    db_host = os.getenv("FB_HOST", "localhost")
    db_port = os.getenv("FB_PORT", "3050")
    db_user = os.getenv("FB_USER", "SYSDBA")
    db_password = os.getenv("FB_PASSWORD", "masterkey")

    db_file = tmp_path / f"join_{uuid.uuid4().hex}.fdb"
    data_source_name = f"{db_host}/{db_port}:{db_file}"

    # setup: create DB
    create_database(
        database=data_source_name,
        user=db_user,
        password=db_password,
        charset="UTF8",
    )

    try:
        yield {"dsn": data_source_name, "user": db_user, "password": db_password}
    finally:
        # teardown: remove file
        try:
            if db_file.exists():
                db_file.unlink()
        except OSError:
            log.exception(f"Could not delete DB file {db_file}")


def test_left_join_filter_on_vs_where(fb_db):
    dsn = fb_db["dsn"]
    user = fb_db["user"]
    password = fb_db["password"]

    with connect(database=dsn, user=user, password=password, charset="UTF8") as db_con:
        cur = db_con.cursor()

        # Schema
        cur.execute("""
            CREATE TABLE a (
                id INTEGER NOT NULL PRIMARY KEY,
                name VARCHAR(20)
            )
        """)
        cur.execute("""
            CREATE TABLE b (
                id INTEGER NOT NULL PRIMARY KEY,
                a_id INTEGER,
                flag SMALLINT
            )
        """)
        db_con.commit()

        # Наполняем таблицы данными
        cur.execute("INSERT INTO a(id, name) VALUES (?, ?)", (1, "a1"))
        cur.execute("INSERT INTO a(id, name) VALUES (?, ?)", (2, "a2"))
        cur.execute("INSERT INTO b(id, a_id, flag) VALUES (?, ?, ?)", (10, 1, 0))
        db_con.commit()

        sql_on = """
                 SELECT a.id, b.id
                 FROM a
                 LEFT JOIN b
                     ON b.a_id = a.id AND b.flag = 1
                 ORDER BY a.id
                 """
        sql_where = """
                    SELECT a.id, b.id
                    FROM a
                    LEFT JOIN b
                        ON b.a_id = a.id
                    WHERE b.flag = 1
                    ORDER BY a.id
                    """

        # Выполняем запросы
        cur.execute(sql_on)
        rows_on = cur.fetchall()

        cur.execute(sql_where)
        rows_where = cur.fetchall()

        # Сравниваем полученные результаты
        assert (rows_on, rows_where) == ([(1, None), (2, None)], [])
