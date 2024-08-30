from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine
from routers import auth, budget

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(budget.router)