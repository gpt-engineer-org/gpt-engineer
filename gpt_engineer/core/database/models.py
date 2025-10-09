# database/models.py
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

# Get database URL from environment or use SQLite as default
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///gpt_engineer.db')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # New fields for email change
    pending_email = Column(String(255), nullable=True)
    email_verification_token = Column(String(255), nullable=True)
    token_created_at = Column(DateTime, nullable=True)

class EmailChangeLog(Base):
    __tablename__ = "email_change_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    old_email = Column(String(255), nullable=False)
    new_email = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)

# Create tables
Base.metadata.create_all(engine)