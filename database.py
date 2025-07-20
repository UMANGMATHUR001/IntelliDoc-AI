import os
import time
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import streamlit as st

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    # Fallback to individual components if DATABASE_URL is not available
    PGHOST = os.getenv("PGHOST", "localhost")
    PGPORT = os.getenv("PGPORT", "5432")
    PGDATABASE = os.getenv("PGDATABASE", "pdf_analyzer")
    PGUSER = os.getenv("PGUSER", "postgres")
    PGPASSWORD = os.getenv("PGPASSWORD", "")
    
    DATABASE_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"

# Create engine with connection pooling and retry logic
engine = create_engine(
    DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    connect_args={
        "connect_timeout": 10,
        "application_name": "pdf_analyzer"
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database tables with retry logic"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                # Create users table
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create documents table
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        filename VARCHAR(500) NOT NULL,
                        content TEXT NOT NULL,
                        summary TEXT,
                        file_size INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                    )
                """))
                
                # Create qa_interactions table
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS qa_interactions (
                        id SERIAL PRIMARY KEY,
                        document_id INTEGER NOT NULL,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                    )
                """))
                
                # Create indexes for better performance
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id)
                """))
                
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_qa_interactions_document_id ON qa_interactions(document_id)
                """))
                
                connection.commit()
                return  # Success, exit the retry loop
                
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"Database connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                st.error(f"Database initialization failed after {max_retries} attempts: {str(e)}")
                raise

def create_user(user_id: str):
    """Create a new user in the database with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                connection.execute(
                    text("INSERT INTO users (user_id) VALUES (:user_id) ON CONFLICT (user_id) DO UPDATE SET last_login = CURRENT_TIMESTAMP"),
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
    """Save a document to the database and return document ID with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
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
                connection.commit()
                doc_id = result.fetchone()[0]
                return doc_id
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                st.error(f"Error saving document after {max_retries} attempts: {str(e)}")
                raise

def get_user_documents(user_id: str) -> list:
    """Get all documents for a specific user"""
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
            
            documents = []
            for row in result:
                documents.append({
                    'id': row[0],
                    'filename': row[1],
                    'content': row[2],
                    'summary': row[3],
                    'file_size': row[4],
                    'created_at': row[5]
                })
            
            return documents
    except Exception as e:
        st.error(f"Error fetching documents: {str(e)}")
        return []

def save_qa_interaction(document_id: int, question: str, answer: str):
    """Save a Q&A interaction to the database"""
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
    """Get Q&A history for a specific document"""
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
                    'question': row[0],
                    'answer': row[1],
                    'created_at': row[2]
                })
            
            return qa_history
    except Exception as e:
        st.error(f"Error fetching Q&A history: {str(e)}")
        return []

def delete_document(document_id: int, user_id: str) -> bool:
    """Delete a document and its associated Q&A interactions"""
    try:
        with engine.connect() as connection:
            # Verify ownership before deletion
            result = connection.execute(
                text("SELECT id FROM documents WHERE id = :doc_id AND user_id = :user_id"),
                {"doc_id": document_id, "user_id": user_id}
            )
            
            if not result.fetchone():
                return False
            
            # Delete Q&A interactions first (foreign key constraint)
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
    """Get user statistics"""
    try:
        with engine.connect() as connection:
            # Get document count
            doc_result = connection.execute(
                text("SELECT COUNT(*) FROM documents WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            doc_count = doc_result.fetchone()[0]
            
            # Get total Q&A interactions
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
            
            return {
                'document_count': doc_count,
                'qa_count': qa_count
            }
    except Exception as e:
        st.error(f"Error getting user stats: {str(e)}")
        return {'document_count': 0, 'qa_count': 0}
