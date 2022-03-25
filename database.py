from contextlib import contextmanager


Article = tuple([int, str, str])

# ---- SQL ----

CREATE_ARTICLES = """CREATE TABLE IF NOT EXISTS articles
(id SERIAL PRIMARY KEY, title TEXT, author TEXT[], date DATE, rubric TEXT, tags TEXT[], word_count INT, url TEXT, date_added DATE);"""

SELECT_ALL_ARTICLES = "SELECT * FROM articles;"

SELECT_BY_TAG = "SELECT * FROM articles WHERE %s = any(tags);"


INSERT_ARTICLE_RETURN_ID = "INSERT INTO articles (title, author, date, rubric, tags, word_count, url, date_added) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"

# ----- DB Access -----

@contextmanager
def get_cursor(connection):
    with connection:
        with connection.cursor() as cursor:
            yield cursor

def create_tables(connection):
    with get_cursor(connection) as cursor:
        cursor.execute(CREATE_ARTICLES)
        # cursor.execute(CREATE_OPTIONS)
        # cursor.execute(CREATE_VOTES)

# --- Articles ---


def create_article(connection, title: str, author: str, date: str, rubric: str, tags: list, word_count: int, url: str, date_added: str):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_ARTICLE_RETURN_ID, (title, author, date, rubric, tags, word_count, url, date_added))

        article_id = cursor.fetchone()[0]
        return article_id


def get_articles(connection) -> list(Article):
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_ALL_ARTICLES)
        return cursor.fetchall()