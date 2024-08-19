from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Budgets).all()

@app.get("/budget/{budget_id}")
async def read_budget(budget_id: int, db: Session = Depends(get_db)):
    budget_model = db.query(models.Budgets).filter(models.Budgets.id == budget_id).first()
    if budget_model is not None:
        return budget_model
    raise http_expection()

def http_expection():
    return HTTPException(status_code=404, detail="Budget not found")