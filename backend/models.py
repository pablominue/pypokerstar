from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Range(Base):
    __tablename__ = "ranges"
    
    id = Column(Integer, primary_key=True)
    player = Column(String, nullable=False)
    category = Column(String, nullable=False)
    position = Column(String, nullable=False)
    name = Column(String, nullable=False)
    range_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class Config:
        orm_mode = True