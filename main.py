from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from auth import get_user_exception, get_current_user


app = FastAPI()

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


@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Budgets).all()

@app.get("/budgets/user")
async def read_all_by_users(user: dict = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Budgets).filter(models.Budgets.owner_id == user.get("id")).all()

@app.get("/budget/{budget_id}")
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

@app.post("/")
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

@app.put("/{budget_id}")
async def update_budget(budget_id: int,
                        budget: Budget,
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
    
    budget_model.name = budget.name
    budget_model.description = budget.description
    budget_model.amount = budget.amount
    budget_model.category = budget.category

    db.add(budget_model)
    db.commit()

    return successful_response(200)

@app.delete("/{budget_id}")
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