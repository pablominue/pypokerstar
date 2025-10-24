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

from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    categories = relationship("Category", back_populates="player", cascade="all, delete-orphan")
    ranges = relationship("Range", back_populates="player_rel", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    player = relationship("Player", back_populates="categories")
    ranges = relationship("Range", back_populates="category_rel", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("player_id", "name", name="_player_category_uc"),)

class Range(Base):
    __tablename__ = "ranges"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    position = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    range_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    player_rel = relationship("Player", back_populates="ranges")
    category_rel = relationship("Category", back_populates="ranges")

    __table_args__ = (UniqueConstraint("player_id", "category_id", "position", "name", name="_range_unique_uc"),)