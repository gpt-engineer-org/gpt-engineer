from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Letter(Base):
    __tablename__ = 'letters'

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String, index=True)
    content = Column(Text)

Base.metadata.create_all(bind=engine)