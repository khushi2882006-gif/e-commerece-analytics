from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(DateTime, nullable=False)
    status = Column(String, default="completed")  # completed / returned / pending
    channel = Column(String, default="web")  # web / mobile / marketplace
    total_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    promo_code = Column(String, nullable=True)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
