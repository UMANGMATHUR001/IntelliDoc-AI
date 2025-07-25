import os
import time
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import streamlit as st


def _make_engine():
    """Create an engine that points to Postgres if DATABASE_URL exists, otherwise SQLite."""
    database_url = os.getenv("DATABASE_URL")

    # Cloud / production: Postgres via DATABASE_URL
    if database_url:
        st.info("🔌 Using PostgreSQL (DATABASE_URL detected)")
        return create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={},  # psycopg2 handles timeouts itself
        )

    # Local dev: SQLite
    sqlite_url = "sqlite:///local.db"
    st.info(f"💾 Using local SQLite database: {sqlite_url}")
    return create_engine(
        sqlite_url,
        echo=False,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False},  # needed for SQLite + Streamlit
    )


engine = _make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _id_col(dialect: str) -> str:
    """Return the appropriate auto-increment PK column definition per dialect."""
    if dialect == "postgresql":
        return "SERIAL PRIMARY KEY"
    # sqlite / others
    return "INTEGER PRIMARY KEY AUTOINCREMENT"


def init_database():
    """Initialize database tables with retry logic, portable across SQLite/Postgres."""
    max_retries = 3
    retry_delay = 2

    dialect = engine.dialect.name
    id_col = _id_col(dialect)

    # NOTE: SQLite doesn't support "ON CONFLICT (user_id) DO UPDATE..." in the same way Postgres does.
    # We handle that logic in create_user() using dialect checks.
    try:
        for attempt in range(max_retries):
            try:
                with engine.connect() as connection:
                    # users
                    connection.execute(text(f"""
                        CREATE TABLE IF NOT EXISTS users (
                            id {id_col},
                            user_id VARCHAR(255) UNIQUE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))

                    # documents
                    # For SQLite, there is no real FOREIGN KEY enforcement unless PRAGMA enabled,
                    # but we'll keep the syntax consistent.
                    connection.execute(text(f"""
                        CREATE TABLE IF NOT EXISTS documents (
                            id {id_col},
                            user_id VARCHAR(255) NOT NULL,
                            filename VARCHAR(500) NOT NULL,
                            content TEXT NOT NULL,
                            summary TEXT,
                            file_size INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))

                    # qa_interactions
                    connection.execute(text(f"""
                        CREATE TABLE IF NOT EXISTS qa_interactions (
                            id {id_col},
                            document_id INTEGER NOT NULL,
                            question TEXT NOT NULL,
                            answer TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))

                    # Indexes (SQLite will just ignore "IF NOT EXISTS" when unsupported forms appear)
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id)
                    """))
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_qa_interactions_document_id ON qa_interactions(document_id)
                    """))

                    connection.commit()
                    return  # success

            except Exception as e:
                if attempt < max_retries - 1:
                    st.warning(
                        f"Database connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    st.error(f"Database initialization failed after {max_retries} attempts: {str(e)}")
                    raise
    except Exception:
        # Re-raise to let the caller stop the app if needed
        raise


def _now():
    return datetime.utcnow()


def create_user(user_id: str):
    """Create or upsert a user."""
    dialect = engine.dialect.name
    max_retries = 3

    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                if dialect == "postgresql":
                    # Postgres upsert
                    connection.execute(
                        text("""
                            INSERT INTO users (user_id, created_at, last_login)
                            VALUES (:user_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            ON CONFLICT (user_id) DO UPDATE SET last_login = CURRENT_TIMESTAMP
                        """),
                        {"user_id": user_id}
                    )
                else:
                    # SQLite fallback: try update, if 0 rows affected, insert
                    result = connection.execute(
                        text("""
                            UPDATE users
                            SET last_login = CURRENT_TIMESTAMP
                            WHERE user_id = :user_id
                        """),
                        {"user_id": user_id}
                    )
                    if result.rowcount == 0:
                        connection.execute(
                            text("""
                                INSERT INTO users (user_id, created_at, last_login)
                                VALUES (:user_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            """),
                            {"user_id": user_id}
                        )

                connection.commit()
                return
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                st.error(f"Error creating user after {max_retries} attempts: {str(e)}")
                raise


def save_document(user_id: str, filename: str, content: str, summary: str, file_size: int) -> int:
    """Save a document and return its ID."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                # RETURNING id works on Postgres; SQLite supports "last_insert_rowid()"
                dialect = engine.dialect.name
                if dialect == "postgresql":
                    result = connection.execute(
                        text("""
                            INSERT INTO documents (user_id, filename, content, summary, file_size)
                            VALUES (:user_id, :filename, :content, :summary, :file_size)
                            RETURNING id
                        """),
                        {
                            "user_id": user_id,
                            "filename": filename,
                            "content": content,
                            "summary": summary,
                            "file_size": file_size
                        }
                    )
                    doc_id = result.fetchone()[0]
                else:
                    connection.execute(
                        text("""
                            INSERT INTO documents (user_id, filename, content, summary, file_size)
                            VALUES (:user_id, :filename, :content, :summary, :file_size)
                        """),
                        {
                            "user_id": user_id,
                            "filename": filename,
                            "content": content,
                            "summary": summary,
                            "file_size": file_size
                        }
                    )
                    # fetch last inserted id in SQLite
                    result = connection.execute(text("SELECT last_insert_rowid()"))
                    doc_id = result.fetchone()[0]

                connection.commit()
                return doc_id
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                st.error(f"Error saving document after {max_retries} attempts: {str(e)}")
                raise


def get_user_documents(user_id: str) -> list:
    """Fetch all documents for a user."""
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    SELECT id, filename, content, summary, file_size, created_at
                    FROM documents
                    WHERE user_id = :user_id
                    ORDER BY created_at DESC
                """),
                {"user_id": user_id}
            )

            docs = []
            for row in result:
                docs.append({
                    "id": row[0],
                    "filename": row[1],
                    "content": row[2],
                    "summary": row[3],
                    "file_size": row[4],
                    "created_at": row[5],
                })
            return docs
    except Exception as e:
        st.error(f"Error fetching documents: {str(e)}")
        return []


def save_qa_interaction(document_id: int, question: str, answer: str):
    """Save a Q&A interaction."""
    try:
        with engine.connect() as connection:
            connection.execute(
                text("""
                    INSERT INTO qa_interactions (document_id, question, answer)
                    VALUES (:document_id, :question, :answer)
                """),
                {
                    "document_id": document_id,
                    "question": question,
                    "answer": answer
                }
            )
            connection.commit()
    except Exception as e:
        st.error(f"Error saving Q&A interaction: {str(e)}")
        raise


def get_document_qa_history(document_id: int) -> list:
    """Get Q&A history for a document."""
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    SELECT question, answer, created_at
                    FROM qa_interactions
                    WHERE document_id = :document_id
                    ORDER BY created_at DESC
                """),
                {"document_id": document_id}
            )

            qa_history = []
            for row in result:
                qa_history.append({
                    "question": row[0],
                    "answer": row[1],
                    "created_at": row[2]
                })
            return qa_history
    except Exception as e:
        st.error(f"Error fetching Q&A history: {str(e)}")
        return []


def delete_document(document_id: int, user_id: str) -> bool:
    """Delete a document and its Q&A."""
    try:
        with engine.connect() as connection:
            # Verify ownership
            result = connection.execute(
                text("SELECT id FROM documents WHERE id = :doc_id AND user_id = :user_id"),
                {"doc_id": document_id, "user_id": user_id}
            )
            if not result.fetchone():
                return False

            # Delete QA first
            connection.execute(
                text("DELETE FROM qa_interactions WHERE document_id = :doc_id"),
                {"doc_id": document_id}
            )
            # Delete document
            connection.execute(
                text("DELETE FROM documents WHERE id = :doc_id"),
                {"doc_id": document_id}
            )

            connection.commit()
            return True
    except Exception as e:
        st.error(f"Error deleting document: {str(e)}")
        return False


def get_user_stats(user_id: str) -> dict:
    """Return simple stats for a user."""
    try:
        with engine.connect() as connection:
            doc_result = connection.execute(
                text("SELECT COUNT(*) FROM documents WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            doc_count = doc_result.fetchone()[0]

            qa_result = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM qa_interactions qi
                    JOIN documents d ON qi.document_id = d.id
                    WHERE d.user_id = :user_id
                """),
                {"user_id": user_id}
            )
            qa_count = qa_result.fetchone()[0]

            return {"document_count": doc_count, "qa_count": qa_count}
    except Exception as e:
        st.error(f"Error getting user stats: {str(e)}")
        return {"document_count": 0, "qa_count": 0}
