from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model for storing user information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, user_id='{self.user_id}')>"
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Document(Base):
    """Document model for storing uploaded PDF documents and their metadata"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey('users.user_id'), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    qa_interactions = relationship("QAInteraction", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', user_id='{self.user_id}')>"
    
    def to_dict(self):
        """Convert document object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'content': self.content,
            'summary': self.summary,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'word_count': len(self.content.split()) if self.content else 0,
            'char_count': len(self.content) if self.content else 0
        }
    
    def get_content_preview(self, length=200):
        """Get a preview of the document content"""
        if not self.content:
            return ""
        
        if len(self.content) <= length:
            return self.content
        
        return self.content[:length] + "..."
    
    def get_summary_preview(self, length=100):
        """Get a preview of the document summary"""
        if not self.summary:
            return "No summary available"
        
        if len(self.summary) <= length:
            return self.summary
        
        return self.summary[:length] + "..."

class QAInteraction(Base):
    """Model for storing question-answer interactions with documents"""
    __tablename__ = 'qa_interactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="qa_interactions")
    
    def __repr__(self):
        return f"<QAInteraction(id={self.id}, document_id={self.document_id})>"
    
    def to_dict(self):
        """Convert QA interaction object to dictionary"""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'question': self.question,
            'answer': self.answer,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'question_preview': self.get_question_preview(),
            'answer_preview': self.get_answer_preview()
        }
    
    def get_question_preview(self, length=100):
        """Get a preview of the question"""
        if not self.question:
            return ""
        
        if len(self.question) <= length:
            return self.question
        
        return self.question[:length] + "..."
    
    def get_answer_preview(self, length=150):
        """Get a preview of the answer"""
        if not self.answer:
            return ""
        
        if len(self.answer) <= length:
            return self.answer
        
        return self.answer[:length] + "..."

# Database schema creation functions
def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def drop_tables(engine):
    """Drop all tables from the database"""
    Base.metadata.drop_all(bind=engine)

# Utility functions for data validation
def validate_user_data(user_data):
    """Validate user data before database insertion"""
    required_fields = ['user_id']
    
    for field in required_fields:
        if field not in user_data or not user_data[field]:
            raise ValueError(f"Missing required field: {field}")
    
    if len(user_data['user_id']) > 255:
        raise ValueError("User ID too long (max 255 characters)")
    
    return True

def validate_document_data(document_data):
    """Validate document data before database insertion"""
    required_fields = ['user_id', 'filename', 'content']
    
    for field in required_fields:
        if field not in document_data or not document_data[field]:
            raise ValueError(f"Missing required field: {field}")
    
    if len(document_data['filename']) > 500:
        raise ValueError("Filename too long (max 500 characters)")
    
    if len(document_data['user_id']) > 255:
        raise ValueError("User ID too long (max 255 characters)")
    
    return True

def validate_qa_data(qa_data):
    """Validate Q&A interaction data before database insertion"""
    required_fields = ['document_id', 'question', 'answer']
    
    for field in required_fields:
        if field not in qa_data or not qa_data[field]:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(qa_data['document_id'], int):
        raise ValueError("Document ID must be an integer")
    
    return True

# Database query helper functions
class DatabaseQueries:
    """Helper class for common database queries"""
    
    @staticmethod
    def get_user_document_count(session, user_id):
        """Get the number of documents for a user"""
        return session.query(Document).filter(Document.user_id == user_id).count()
    
    @staticmethod
    def get_user_qa_count(session, user_id):
        """Get the total number of Q&A interactions for a user"""
        return session.query(QAInteraction).join(Document).filter(Document.user_id == user_id).count()
    
    @staticmethod
    def get_recent_documents(session, user_id, limit=10):
        """Get recent documents for a user"""
        return session.query(Document).filter(
            Document.user_id == user_id
        ).order_by(Document.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_document_with_qa(session, document_id, user_id):
        """Get a document with its Q&A interactions"""
        document = session.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()
        
        if document:
            qa_interactions = session.query(QAInteraction).filter(
                QAInteraction.document_id == document_id
            ).order_by(QAInteraction.created_at.desc()).all()
            
            document_dict = document.to_dict()
            document_dict['qa_interactions'] = [qa.to_dict() for qa in qa_interactions]
            
            return document_dict
        
        return None
    
    @staticmethod
    def search_documents(session, user_id, search_term):
        """Search documents by filename or content"""
        return session.query(Document).filter(
            Document.user_id == user_id,
            (Document.filename.ilike(f"%{search_term}%") | 
             Document.content.ilike(f"%{search_term}%"))
        ).order_by(Document.created_at.desc()).all()
