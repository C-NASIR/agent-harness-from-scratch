import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATABASE = "customer_service_agent_database.db"
ARTICLES_DIR = Path(__file__).resolve().parent.parent / "articles"


def init():
    db_init()
    init_knowledge_articles()

def db_init():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY, 
                history TEXT NOT NULL,
                context TEXT NOT NULL
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_articles (
                id TEXT PRIMARY KEY, 
                title TEXT NOT NULL, 
                body TEXT NOT NULL
            )
        """)


def init_knowledge_articles():
    with get_db() as db:
        existing_ids = {
            row[0] for row in db.execute("SELECT id FROM knowledge_articles")
        }

        for article in ARTICLES_DIR.glob("*.md"):
            article_id = article.stem
            if article_id in existing_ids: continue

            title, _, body = article.read_text(encoding="utf-8").partition("\n")
            title = title.removeprefix("# ").strip()
            body = body.strip()

            db.execute(""" 
                INSERT OR IGNORE INTO knowledge_articles (id, title, body)
                VALUES (?, ?, ?)
            """, (article_id, title, body))


@contextmanager
def get_db():
    db = sqlite3.connect(DATABASE)

    try:
        with db:
            yield db 
    finally:
        db.close()
