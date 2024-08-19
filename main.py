from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

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


@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Budgets).all()

@app.get("/budget/{budget_id}")
async def read_budget(budget_id: int, db: Session = Depends(get_db)):
    budget_model = db.query(models.Budgets).filter(models.Budgets.id == budget_id).first()
    if budget_model is not None:
        return budget_model
    raise http_expection()

@app.post("/")
async def create_budget(budget: Budget, db: Session = Depends(get_db)):
    budget_model = models.Budgets()
    budget_model.name = budget.name
    budget_model.description = budget.description
    budget_model.amount = budget.amount

    db.add(budget_model)
    db.commit()

    return {
        'status': 201,
        'transaction': 'Successful'
    }

@app.put("/{budget_id}")
async def update_budget(budget_id: int, budget: Budget, db: Session = Depends(get_db)):
    budget_model = db.query(models.Budgets).filter(models.Budgets.id == budget_id).first()
    
    if budget_model is None:
        raise http_expection()
    
    budget_model.name = budget.name
    budget_model.description = budget.description
    budget_model.amount = budget.amount

    db.add(budget_model)
    db.commit()

    return {
        'status': 200,
        'transaction': 'Successful'
    }

def http_expection():
    return HTTPException(status_code=404, detail="Budget not found")