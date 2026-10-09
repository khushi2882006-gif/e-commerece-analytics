"""
Seed script: generates realistic mock data and loads it into analytics.db.
Idempotent — clears all tables and reseeds on every run.
Run: python seed.py
"""
import sys
import os
import random
from datetime import datetime, timedelta, date

sys.path.insert(0, os.path.dirname(__file__))

from faker import Faker
from database import engine, SessionLocal, Base
from models.customer import Customer
from models.product import Product
from models.order import Order, OrderItem
from models.inventory import InventoryEvent
from models.shipment import ShipmentEvent
from models.marketing import MarketingSpend

fake = Faker()
random.seed(42)
Faker.seed(42)

# ── Constants ──────────────────────────────────────────────────────────────
NUM_CUSTOMERS = 200
NUM_PRODUCTS = 50
NUM_ORDERS = 1200
CARRIERS = ["FedEx", "UPS", "DHL", "USPS", "BlueDart"]
CHANNELS = ["web", "mobile", "marketplace"]
PROMO_CODES = ["SAVE10", "SUMMER20", "FLASH15", "WELCOME5", None, None, None]
MARKETING_CHANNELS = ["google", "facebook", "email", "influencer"]

CATEGORIES = [
    "Electronics", "Clothing", "Home & Kitchen", "Sports", "Beauty",
    "Books", "Toys", "Automotive", "Garden", "Pet Supplies"
]

PRODUCT_NAMES = {
    "Electronics": ["Wireless Headphones", "Smart Speaker", "USB Hub", "Laptop Stand", "Webcam", "LED Desk Lamp"],
    "Clothing": ["Cotton T-Shirt", "Denim Jeans", "Winter Jacket", "Sports Shorts", "Formal Shirt"],
    "Home & Kitchen": ["Coffee Maker", "Non-stick Pan", "Cutting Board", "Water Filter", "Storage Organizer"],
    "Sports": ["Yoga Mat", "Resistance Bands", "Water Bottle", "Running Shoes", "Jump Rope"],
    "Beauty": ["Face Serum", "Moisturizer SPF50", "Hair Oil", "Vitamin C Cream", "Lip Balm"],
    "Books": ["Python Programming", "Business Strategy", "Self Help Guide", "Cooking Basics", "History Atlas"],
    "Toys": ["Building Blocks", "RC Car", "Puzzle Set", "Doll House", "Board Game"],
    "Automotive": ["Car Vacuum", "Seat Cover", "Dash Cam", "Phone Mount", "Tire Gauge"],
    "Garden": ["Plant Pots Set", "Garden Gloves", "Watering Can", "Seed Kit", "Pruning Shears"],
    "Pet Supplies": ["Dog Leash", "Cat Toy Set", "Pet Bed", "Food Bowl", "Grooming Brush"],
}

NOW = datetime.utcnow()
YEAR_AGO = NOW - timedelta(days=365)


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def create_tables():
    Base.metadata.create_all(bind=engine)


def clear_tables(db):
    db.query(ShipmentEvent).delete()
    db.query(InventoryEvent).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(MarketingSpend).delete()
    db.query(Customer).delete()
    db.query(Product).delete()
    db.commit()


def seed_customers(db) -> list[Customer]:
    tiers = ["bronze"] * 120 + ["silver"] * 60 + ["gold"] * 20
    random.shuffle(tiers)
    customers = []
    emails_used = set()
    for i in range(NUM_CUSTOMERS):
        email = fake.email()
        while email in emails_used:
            email = fake.email()
        emails_used.add(email)
        c = Customer(
            name=fake.name(),
            email=email,
            city=fake.city(),
            country=fake.country(),
            tier=tiers[i],
            created_at=random_date(YEAR_AGO, NOW),
        )
        customers.append(c)
    db.add_all(customers)
    db.commit()
    for c in customers:
        db.refresh(c)
    return customers


def seed_products(db) -> list[Product]:
    products = []
    for category, names in PRODUCT_NAMES.items():
        for name in names:
            price = round(random.uniform(10, 500), 2)
            cost = round(price * random.uniform(0.35, 0.65), 2)
            stock = random.randint(0, 300)
            p = Product(
                name=name,
                category=category,
                unit_price=price,
                cost_price=cost,
                stock_quantity=stock,
            )
            products.append(p)
    # Trim/pad to NUM_PRODUCTS
    products = products[:NUM_PRODUCTS]
    db.add_all(products)
    db.commit()
    for p in products:
        db.refresh(p)
    return products


def seed_orders(db, customers: list[Customer], products: list[Product]):
    orders = []
    order_items = []
    shipments = []
    inventory_events = []

    statuses = ["completed"] * 80 + ["returned"] * 12 + ["pending"] * 8
    ship_statuses = ["delivered"] * 82 + ["failed"] * 8 + ["in-transit"] * 10

    for _ in range(NUM_ORDERS):
        customer = random.choice(customers)
        order_date = random_date(YEAR_AGO, NOW)
        status = random.choice(statuses)
        channel = random.choice(CHANNELS)
        promo = random.choice(PROMO_CODES)

        discount_pct = 0.0
        if promo == "SAVE10":
            discount_pct = 0.10
        elif promo == "SUMMER20":
            discount_pct = 0.20
        elif promo == "FLASH15":
            discount_pct = 0.15
        elif promo == "WELCOME5":
            discount_pct = 0.05

        # 1–4 items per order
        num_items = random.randint(1, 4)
        selected_products = random.sample(products, min(num_items, len(products)))
        subtotal = 0.0
        for prod in selected_products:
            qty = random.randint(1, 3)
            line_total = round(prod.unit_price * qty, 2)
            subtotal += line_total
            order_items.append(
                OrderItem(product_id=prod.id, quantity=qty, unit_price=prod.unit_price)
            )
            # inventory sale event
            inventory_events.append(
                InventoryEvent(
                    product_id=prod.id,
                    event_type="sale",
                    quantity_change=-qty,
                    event_date=order_date,
                )
            )

        discount_amount = round(subtotal * discount_pct, 2)
        total_amount = round(subtotal - discount_amount, 2)

        order = Order(
            customer_id=customer.id,
            order_date=order_date,
            status=status,
            channel=channel,
            total_amount=total_amount,
            discount_amount=discount_amount,
            promo_code=promo,
        )
        orders.append((order, order_items[-num_items:], selected_products, order_date))

    # Flush orders first to get IDs
    flat_orders = [o for o, _, _, _ in orders]
    db.add_all(flat_orders)
    db.flush()

    all_items = []
    all_shipments = []
    for order, items, prods, order_date in orders:
        for item in items:
            item.order_id = order.id
            all_items.append(item)

        # Shipment
        carrier = random.choice(CARRIERS)
        ship_status = random.choice(ship_statuses)
        shipped_date = order_date + timedelta(days=random.randint(1, 3))
        delivered_date = None
        if ship_status == "delivered":
            delivered_date = shipped_date + timedelta(days=random.randint(1, 7))
        elif ship_status == "failed":
            delivered_date = None

        all_shipments.append(
            ShipmentEvent(
                order_id=order.id,
                carrier=carrier,
                shipped_date=shipped_date,
                delivered_date=delivered_date,
                status=ship_status,
            )
        )

    db.add_all(all_items)
    db.add_all(all_shipments)
    db.commit()

    # Restock events — random monthly restocks per product
    restock_events = []
    for prod in products:
        # 3–8 restock events per product over the year
        for _ in range(random.randint(3, 8)):
            restock_date = random_date(YEAR_AGO, NOW)
            restock_qty = random.randint(50, 200)
            restock_events.append(
                InventoryEvent(
                    product_id=prod.id,
                    event_type="restock",
                    quantity_change=restock_qty,
                    event_date=restock_date,
                )
            )
    db.add_all(inventory_events)
    db.add_all(restock_events)
    db.commit()


def seed_marketing(db):
    records = []
    current = YEAR_AGO.replace(day=1)
    while current <= NOW:
        for channel in MARKETING_CHANNELS:
            spend = round(random.uniform(500, 5000), 2)
            records.append(
                MarketingSpend(
                    channel=channel,
                    spend_amount=spend,
                    period_date=current.date(),
                )
            )
        # move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    db.add_all(records)
    db.commit()


def main():
    print("Creating tables...")
    create_tables()
    db = SessionLocal()
    try:
        print("Clearing existing data...")
        clear_tables(db)
        print(f"Seeding {NUM_CUSTOMERS} customers...")
        customers = seed_customers(db)
        print(f"Seeding {NUM_PRODUCTS} products...")
        products = seed_products(db)
        print(f"Seeding {NUM_ORDERS} orders with items + shipments + inventory events...")
        seed_orders(db, customers, products)
        print("Seeding marketing spend records...")
        seed_marketing(db)
        print("✅ Seeding complete!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
