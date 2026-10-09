from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database import Base


class InventoryEvent(Base):
    __tablename__ = "inventory_events"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    event_type = Column(String, nullable=False)  # restock / sale
    quantity_change = Column(Integer, nullable=False)
    event_date = Column(DateTime, nullable=False)
