from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, SessionLocal, Base
from models.customer import Customer
from models.product import Product
from models.order import Order, OrderItem
from models.inventory import InventoryEvent
from models.shipment import ShipmentEvent
from models.marketing import MarketingSpend
import routers.auth as auth_router
import routers.sales as sales_router
import routers.customers as customers_router
import routers.products as products_router
import routers.inventory as inventory_router
import routers.marketing as marketing_router
import routers.fulfillment as fulfillment_router

app = FastAPI(title="E-Commerce Analytics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router.router)
app.include_router(sales_router.router)
app.include_router(customers_router.router)
app.include_router(products_router.router)
app.include_router(inventory_router.router)
app.include_router(marketing_router.router)
app.include_router(fulfillment_router.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def startup():
    # Create tables
    Base.metadata.create_all(bind=engine)
    # Auto-seed if DB is empty
    db = SessionLocal()
    try:
        count = db.query(Customer).count()
        if count == 0:
            import seed
            seed.main()
    finally:
        db.close()
