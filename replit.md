# AI PDF Summarizer & Q&A System

## Overview

This is a Streamlit-based web application that allows users to upload PDF documents, generate AI-powered summaries, and ask questions about the document content. The system uses OpenAI's API for text processing and maintains user sessions with document history stored in a PostgreSQL database.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Frontend**: Streamlit web interface providing file upload, summary generation, and Q&A functionality
- **Backend**: Python modules handling authentication, database operations, PDF processing, and AI integration
- **Database**: PostgreSQL for persistent storage of users, documents, and Q&A interactions
- **AI Service**: OpenAI API integration for text summarization and question answering
- **File Processing**: PyMuPDF for PDF text extraction and validation

## Key Components

### Core Modules

1. **app.py** - Main Streamlit application entry point and UI orchestration
2. **auth.py** - Session-based authentication system with temporary user IDs
3. **database.py** - PostgreSQL database operations using SQLAlchemy raw SQL
4. **models.py** - SQLAlchemy ORM models for User, Document, and QAInteraction entities
5. **ai_service.py** - OpenAI API integration for summarization and Q&A
6. **pdf_processor.py** - PDF validation and text extraction using PyMuPDF
7. **utils.py** - Utility functions for file formatting and text processing

### Data Models

- **Users**: Stores user sessions with unique user IDs and timestamps
- **Documents**: Stores uploaded PDF metadata, extracted content, and generated summaries
- **QA Interactions**: Records questions asked and AI-generated answers for each document

## Data Flow

1. **Authentication**: Users are automatically authenticated with temporary session-based user IDs
2. **Document Upload**: PDFs are validated, text is extracted using PyMuPDF, and content is stored in PostgreSQL
3. **Intelligent Chunking**: Large documents are split into 1000-1500 word chunks for efficient processing
4. **Summarization**: Document chunks are sent to Google Gemini AI with configurable length parameters (short/medium/long)
5. **Q&A Processing**: User questions are processed against document content using Google Gemini AI with smart section searching
5. **History Tracking**: All interactions are stored in the database and can be retrieved per user session

## External Dependencies

### Required Services
- **Google Gemini AI**: Free cloud AI service for text summarization and question answering (requires GEMINI_API_KEY)

### Python Libraries
- **streamlit**: Web application framework
- **sqlalchemy**: Database ORM and raw SQL operations
- **PyMuPDF (fitz)**: PDF text extraction and validation
- **google-genai**: Google Gemini API client for cloud AI inference
- **requests**: HTTP client for API communications

### Database
- **PostgreSQL**: Primary data storage (configurable via DATABASE_URL or individual PG* environment variables)

## Deployment Strategy

The application is designed for Replit deployment with the following considerations:

### Environment Variables Required
- `DATABASE_URL`: Complete PostgreSQL connection string, OR individual components:
  - `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`

### Service Requirements
- **Google Gemini API**: Free tier provides 15 requests per minute, sufficient for personal use

### Authentication Strategy
- Currently uses temporary session-based authentication suitable for demo purposes
- Architecture supports future integration with Replit Auth or other authentication providers
- User sessions are maintained via Streamlit session state

### Database Initialization
- Automatic table creation on startup using raw SQL DDL statements
- Support for both complete DATABASE_URL and component-based PostgreSQL configuration
- Fallback handling for missing database configuration

### Key Architectural Decisions

1. **Session-based Authentication**: Chosen for simplicity in demo environment, easily replaceable with proper auth systems
2. **Raw SQL + ORM Hybrid**: Uses SQLAlchemy raw SQL for table creation and ORM models for data structure definition
3. **Google Gemini Integration**: Free cloud AI service with intelligent text chunking for optimal performance
4. **PyMuPDF for PDF Processing**: Reliable text extraction with built-in validation capabilities
5. **Streamlit for UI**: Rapid development framework suitable for data science applications

The system is structured to be easily extensible while maintaining clear separation between data processing, AI services, and user interface components.