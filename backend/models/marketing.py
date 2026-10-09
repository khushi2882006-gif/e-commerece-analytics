from sqlalchemy import Column, Integer, String, Float, Date
from database import Base


class MarketingSpend(Base):
    __tablename__ = "marketing_spend"

    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String, nullable=False)  # google / facebook / email / influencer
    spend_amount = Column(Float, nullable=False)
    period_date = Column(Date, nullable=False)  # monthly granularity (1st of each month)
