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
from .models import Base, Player, Category, Range as RangeModel
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

class PlayerCreate(BaseModel):
    name: str

class CategoryCreate(BaseModel):
    player: str
    name: str
@app.post("/players")
def create_player(p: PlayerCreate, db: Session = Depends(get_db)):
    existing = db.query(Player).filter(Player.name == p.name).first()
    if existing:
        return {"id": existing.id, "name": existing.name}
    new = Player(name=p.name)
    db.add(new)
    db.commit()
    db.refresh(new)
    return {"id": new.id, "name": new.name}

@app.get("/players")
def list_players(db: Session = Depends(get_db)):
    rows = db.query(Player).order_by(Player.name).all()
    return [r.name for r in rows]

# Categories endpoints
@app.post("/categories")
def create_category(c: CategoryCreate, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.name == c.player).first()
    if not player:
        player = Player(name=c.player)
        db.add(player)
        db.commit()
        db.refresh(player)
    existing = db.query(Category).filter(Category.player_id == player.id, Category.name == c.name).first()
    if existing:
        return {"id": existing.id, "name": existing.name}
    new = Category(player_id=player.id, name=c.name)
    db.add(new)
    db.commit()
    db.refresh(new)
    return {"id": new.id, "name": new.name}

@app.get("/categories")
def list_categories(player: str = "default", db: Session = Depends(get_db)):
    player_row = db.query(Player).filter(Player.name == player).first()
    if not player_row:
        return []
    rows = db.query(Category).filter(Category.player_id == player_row.id).order_by(Category.name).all()
    return [r.name for r in rows]

# Names: list saved range names for player/category/position
@app.get("/names")
def list_names(player: str = "default", category: str = "Ranges", position: str = "UTG", db: Session = Depends(get_db)):
    player_row = db.query(Player).filter(Player.name == player).first()
    if not player_row:
        return []
    cat = db.query(Category).filter(Category.player_id == player_row.id, Category.name == category).first()
    if not cat:
        return []
    rows = db.query(RangeModel).filter(RangeModel.player_id == player_row.id, RangeModel.category_id == cat.id, RangeModel.position == position).order_by(RangeModel.name).all()
    return [r.name for r in rows]

# Tree explorer for UI
@app.get("/ranges/tree")
def ranges_tree(player: t.Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(RangeModel)
    if player:
        player_row = db.query(Player).filter(Player.name == player).first()
        if not player_row:
            return {}
        q = q.filter(RangeModel.player_id == player_row.id)
    rows = q.all()
    tree: t.Dict[str, t.Dict[str, t.Dict[str, t.List[str]]]] = {}
    for r in rows:
        p = r.player_rel.name
        pos = r.position
        cat = r.category_rel.name
        tree.setdefault(p, {}).setdefault(pos, {}).setdefault(cat, []).append(r.name)
    return tree

# Ranges CRUD (save/load/list/delete)
@app.post("/ranges/save")
def save_range(range_data: RangeCreate, db: Session = Depends(get_db)):
    # ensure player & category
    player_row = db.query(Player).filter(Player.name == range_data.player).first()
    if not player_row:
        player_row = Player(name=range_data.player)
        db.add(player_row)
        db.commit()
        db.refresh(player_row)
    cat_row = db.query(Category).filter(Category.player_id == player_row.id, Category.name == range_data.category).first()
    if not cat_row:
        cat_row = Category(player_id=player_row.id, name=range_data.category)
        db.add(cat_row)
        db.commit()
        db.refresh(cat_row)

    existing = db.query(RangeModel).filter(
        RangeModel.player_id == player_row.id,
        RangeModel.category_id == cat_row.id,
        RangeModel.position == range_data.position,
        RangeModel.name == range_data.name
    ).first()

    if existing:
        existing.range_data = range_data.cardRange
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return {"status": "updated", "range": RangeResponse(
            id=existing.id,
            player=player_row.name,
            category=cat_row.name,
            position=existing.position,
            name=existing.name,
            cardRange=existing.range_data,
            created_at=existing.created_at,
            updated_at=existing.updated_at
        ).dict()}
    new = RangeModel(
        player_id=player_row.id,
        category_id=cat_row.id,
        position=range_data.position,
        name=range_data.name,
        range_data=range_data.cardRange
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return {"status": "created", "range": RangeResponse(
        id=new.id,
        player=player_row.name,
        category=cat_row.name,
        position=new.position,
        name=new.name,
        cardRange=new.range_data,
        created_at=new.created_at,
        updated_at=new.updated_at
    ).dict()}

@app.get("/ranges/load")
def load_range(player: str = "default", category: str = "Ranges", position: str = "UTG", name: str = None, db: Session = Depends(get_db)):
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    player_row = db.query(Player).filter(Player.name == player).first()
    if not player_row:
        raise HTTPException(status_code=404, detail="player not found")
    cat_row = db.query(Category).filter(Category.player_id == player_row.id, Category.name == category).first()
    if not cat_row:
        raise HTTPException(status_code=404, detail="category not found")
    r = db.query(RangeModel).filter(
        RangeModel.player_id == player_row.id,
        RangeModel.category_id == cat_row.id,
        RangeModel.position == position,
        RangeModel.name == name
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="range not found")
    return {
        "id": r.id,
        "player": player_row.name,
        "category": cat_row.name,
        "position": r.position,
        "name": r.name,
        "cardRange": r.range_data,
        "created_at": r.created_at,
        "updated_at": r.updated_at
    }

@app.get("/ranges/list")
def list_ranges(player: str = "default", category: str = "Ranges", position: t.Optional[str] = None, db: Session = Depends(get_db)):
    player_row = db.query(Player).filter(Player.name == player).first()
    if not player_row:
        return {"ranges": []}
    cat_row = db.query(Category).filter(Category.player_id == player_row.id, Category.name == category).first()
    if not cat_row:
        return {"ranges": []}
    q = db.query(RangeModel).filter(RangeModel.player_id == player_row.id, RangeModel.category_id == cat_row.id)
    if position:
        q = q.filter(RangeModel.position == position)
    rows = q.all()
    out = []
    for r in rows:
        out.append({
            "id": r.id,
            "name": r.name,
            "position": r.position,
            "player": player_row.name,
            "category": cat_row.name,
            "cardRange": r.range_data,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        })
    return {"ranges": out}

@app.delete("/ranges/delete")
def delete_range(range_data: RangeCreate, db: Session = Depends(get_db)):
    player_row = db.query(Player).filter(Player.name == range_data.player).first()
    if not player_row:
        raise HTTPException(status_code=404, detail="player not found")
    cat_row = db.query(Category).filter(Category.player_id == player_row.id, Category.name == range_data.category).first()
    if not cat_row:
        raise HTTPException(status_code=404, detail="category not found")
    r = db.query(RangeModel).filter(
        RangeModel.player_id == player_row.id,
        RangeModel.category_id == cat_row.id,
        RangeModel.position == range_data.position,
        RangeModel.name == range_data.name
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="range not found")
    db.delete(r)
    db.commit()
    return {"status": "deleted"}