from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tariff(Base):
  __tablename__ = "tariffs"
  id = Column(Integer, primary_key=True, index=True)
  cargo_type = Column(String, nullable=False)
  rate = Column(Float, nullable=False)
  date = Column(Date, nullable=False)