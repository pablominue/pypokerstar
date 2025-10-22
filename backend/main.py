from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import typing as t
from datetime import datetime
from models import Base, Range
from pydantic import BaseModel
import os

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ranges.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RangeCreate(BaseModel):
    player: str
    category: str
    position: str
    name: str
    cardRange: dict

class RangeResponse(BaseModel):
    id: int
    player: str
    category: str
    position: str
    name: str
    range_data: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

@app.post("/ranges/save")
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
            return RangeResponse.from_orm(existing)
        
        db.add(db_range)
        db.commit()
        db.refresh(db_range)
        return RangeResponse.from_orm(db_range)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ranges/load")
async def load_range(
    player: str = "default",
    category: str = "Ranges",
    position: str = "UTG",
    name: str = None,
    db: Session = Depends(get_db)
):
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    
    range_data = db.query(Range).filter(
        Range.player == player,
        Range.category == category,
        Range.position == position,
        Range.name == name
    ).first()
    
    if not range_data:
        raise HTTPException(status_code=404, detail="Range not found")
    
    return RangeResponse.from_orm(range_data)

@app.get("/ranges/list")
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
        "ranges": [RangeResponse.from_orm(r) for r in ranges]
    }

@app.delete("/ranges/delete")
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
