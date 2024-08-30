import sys
sys.path.append("..")

from fastapi import Depends, HTTPException, APIRouter
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from .auth import get_user_exception, get_current_user


router = APIRouter()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Budget(BaseModel):
    name: str
    description: Optional[str]
    amount: int = Field(gt=0)
    category: Optional[str]

class BudgetUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    amount: Optional[int] = Field(gt=0)
    category: Optional[str]


@router.get("/budget")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Budgets).all()

@router.get("/budget/user")
async def read_all_by_users(user: dict = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Budgets).filter(models.Budgets.owner_id == user.get("id")).all()

@router.get("/budget/read/{budget_id}")
async def read_budget(budget_id: int,
                      user:dict = Depends(get_current_user), 
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    budget_model = db.query(models.Budgets)\
        .filter(models.Budgets.id == budget_id)\
        .filter(models.Budgets.owner_id == user.get("id"))\
        .first()
    if budget_model is not None:
        return budget_model
    raise http_expection()

@router.get("/budget/search")
async def search_budget(keyword: str, db: Session = Depends(get_db)):
    results = db.query(models.Budgets).filter(
        (models.Budgets.name.ilike(f"%{keyword}%")) |
        (models.Budgets.description.ilike(f"%{keyword}%")) |
        (models.Budgets.category.ilike(f"%{keyword}%"))
    ).all()

    return results

@router.post("/budget/create")
async def create_budget(budget: Budget,
                        user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    budget_model = models.Budgets()
    budget_model.name = budget.name
    budget_model.description = budget.description
    budget_model.amount = budget.amount
    budget_model.category = budget.category
    budget_model.owner_id = user.get("id")

    db.add(budget_model)
    db.commit()

    return successful_response(201)

@router.put("/budget/update/{budget_id}")
async def update_budget(budget_id: int,
                        budget: BudgetUpdate,
                        user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    
    budget_model = db.query(models.Budgets)\
        .filter(models.Budgets.id == budget_id)\
        .filter(models.Budgets.owner_id == user.get("id"))\
        .first()
    
    if budget_model is None:
        raise http_expection()
    
    if budget.name is not None and budget.name != "string":
        budget_model.name = budget.name 
    if budget.description is not None and budget.description != "string":
        budget_model.description = budget.description
    if budget.amount is not None and budget.amount != 1:
        budget_model.amount = budget.amount 
    if budget.category is not None and budget.category != "string":
        budget_model.category = budget.category

    db.add(budget_model)
    db.commit()

    return successful_response(200)

@router.delete("/budget/delete/{budget_id}")
async def delete_budget(budget_id: int,
                        user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    
    budget_model = db.query(models.Budgets)\
        .filter(models.Budgets.id == budget_id)\
        .filter(models.Budgets.owner_id == user.get("id"))\
        .first()

    if budget_model is None:
        raise http_expection()
    
    db.query(models.Budgets).filter(models.Budgets.id == budget_id).delete()
    db.commit()

    return successful_response(200) 

def http_expection():
    return HTTPException(status_code=404, detail="Budget not found")

def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }