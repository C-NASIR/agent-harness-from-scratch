from src.db import get_db


def load_knowledge_articles():
    with get_db() as db:
        articles = db.execute("SELECT id, title, body FROM knowledge_articles").fetchall()
        return articles