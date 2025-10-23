from sqlalchemy import Column, Integer, String, DateTime, JSON, func, Text
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Range(Base):
    __tablename__ = "ranges"

    id = Column(Integer, primary_key=True, index=True)
    # Specify length for VARCHAR columns (MySQL requires a length)
    player = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    position = Column(String(50), nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)

    # If using MySQL 5.7+ you can use JSON; otherwise use Text and serialize manually
    try:
        range_data = Column(JSON, nullable=False)
    except Exception:
        range_data = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)