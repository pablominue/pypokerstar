from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from typing import Any, Dict, Optional

from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import typing as t
from datetime import datetime
from .models import Base, Range
from pydantic import BaseModel
import os

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ranges.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000"
    ],  # usa ["*"] solo en desarrollo si necesitas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RangeCreate(BaseModel):
    player: str
    category: str
    position: t.Optional[str] = "UTG"
    name: str
    cardRange: Dict[str, Any]

class RangeResponse(BaseModel):
    id: int
    player: str
    category: str
    position: str
    name: str
    cardRange: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

@app.post("/api/ranges/save")
async def save_range(range_data: RangeCreate, db: Session = Depends(get_db)):
    try:
        db_range = Range(
            player=range_data.player,
            category=range_data.category,
            position=range_data.position,
            name=range_data.name,
            range_data=range_data.cardRange
        )
        
        # Check if range already exists
        existing = db.query(Range).filter(
            Range.player == range_data.player,
            Range.category == range_data.category,
            Range.position == range_data.position,
            Range.name == range_data.name
        ).first()
        
        if existing:
            existing.range_data = range_data.cardRange
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return {
                "id": existing.id,
                "player": existing.player,
                "category": existing.category,
                "position": existing.position,
                "name": existing.name,
                "cardRange": existing.range_data,
                "created_at": existing.created_at,
                "updated_at": existing.updated_at,
            }
        
        db.add(db_range)
        db.commit()
        db.refresh(db_range)
        return {
            "id": db_range.id,
            "player": db_range.player,
            "category": db_range.category,
            "position": db_range.position,
            "name": db_range.name,
            "cardRange": db_range.range_data,
            "created_at": db_range.created_at,
            "updated_at": db_range.updated_at,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ranges/load")
async def load_range(
    player: str = "default",
    category: str = "Ranges",
    position: str = "UTG",
    name: str = None,
    db: Session = Depends(get_db)
):
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    
    range_row = db.query(Range).filter(
        Range.player == player,
        Range.category == category,
        Range.position == position,
        Range.name == name
    ).first()
    
    if not range_row:
        raise HTTPException(status_code=404, detail="Range not found")
    
    return {
        "id": range_row.id,
        "player": range_row.player,
        "category": range_row.category,
        "position": range_row.position,
        "name": range_row.name,
        "cardRange": range_row.range_data,
        "created_at": range_row.created_at,
        "updated_at": range_row.updated_at,
    }

@app.get("/api/ranges/list")
async def list_ranges(
    player: str = "default",
    category: str = "Ranges",
    position: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Range).filter(
        Range.player == player,
        Range.category == category
    )
    
    if position:
        query = query.filter(Range.position == position)
    
    ranges = query.all()
    return {
        "ranges": [
            {
                "id": r.id,
                "player": r.player,
                "category": r.category,
                "position": r.position,
                "name": r.name,
                "cardRange": r.range_data,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            for r in ranges
        ]
    }

@app.delete("/api/ranges/delete")
async def delete_range(
    range_data: RangeCreate,
    db: Session = Depends(get_db)
):
    range_to_delete = db.query(Range).filter(
        Range.player == range_data.player,
        Range.category == range_data.category,
        Range.position == range_data.position,
        Range.name == range_data.name
    ).first()
    
    if not range_to_delete:
        raise HTTPException(status_code=404, detail="Range not found")
    
    db.delete(range_to_delete)
    db.commit()
    return {"status": "success", "message": "Range deleted"}