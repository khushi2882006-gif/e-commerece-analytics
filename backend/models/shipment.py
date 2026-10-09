from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database import Base


class ShipmentEvent(Base):
    __tablename__ = "shipment_events"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    carrier = Column(String, nullable=False)
    shipped_date = Column(DateTime, nullable=True)
    delivered_date = Column(DateTime, nullable=True)
    status = Column(String, default="delivered")  # delivered / failed / in-transit
