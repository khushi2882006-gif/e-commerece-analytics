from sqlalchemy import Column, Integer, String, DateTime
from database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    city = Column(String)
    country = Column(String)
    tier = Column(String, default="bronze")  # bronze / silver / gold
    created_at = Column(DateTime, nullable=False)
