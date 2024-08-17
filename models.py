from sqlalchemy import Boolean, Column, Integer, String
from database import Base

class Budgets(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    amount = Column(float)