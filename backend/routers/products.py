from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/products", tags=["products"])


def parse_dates(start_date, end_date):
    now = datetime.utcnow()
    start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else now - timedelta(days=30)
    end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else now
    end = end.replace(hour=23, minute=59, second=59)
    return start, end


@router.get("/kpis")
def get_product_kpis(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    total_products = db.execute(text("SELECT COUNT(*) FROM products")).scalar() or 0
    total_units = db.execute(
        text("""
            SELECT COALESCE(SUM(oi.quantity), 0)
            FROM order_items oi JOIN orders o ON o.id = oi.order_id
            WHERE o.order_date >= :s AND o.order_date <= :e AND o.status != 'returned'
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).scalar() or 0

    top_category = db.execute(
        text("""
            SELECT p.category, SUM(oi.quantity * oi.unit_price) as rev
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            JOIN products p ON p.id = oi.product_id
            WHERE o.order_date >= :s AND o.order_date <= :e AND o.status != 'returned'
            GROUP BY p.category ORDER BY rev DESC LIMIT 1
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).fetchone()

    avg_price = db.execute(
        text("""
            SELECT AVG(oi.unit_price)
            FROM order_items oi JOIN orders o ON o.id = oi.order_id
            WHERE o.order_date >= :s AND o.order_date <= :e AND o.status != 'returned'
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).scalar() or 0

    return {
        "total_products": total_products,
        "total_units_sold": int(total_units),
        "top_category": top_category[0] if top_category else "N/A",
        "avg_sell_price": round(avg_price, 2),
    }


@router.get("/top-selling")
def get_top_selling(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT p.name, p.category,
                   SUM(oi.quantity * oi.unit_price) as revenue,
                   SUM(oi.quantity) as units_sold
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            JOIN products p ON p.id = oi.product_id
            WHERE o.order_date >= :s AND o.order_date <= :e AND o.status != 'returned'
            GROUP BY p.id ORDER BY revenue DESC LIMIT :limit
        """),
        {"s": start.isoformat(), "e": end.isoformat(), "limit": limit},
    ).fetchall()
    return [{"name": r[0], "category": r[1], "revenue": round(r[2], 2), "units_sold": r[3]} for r in rows]


@router.get("/by-category")
def get_by_category(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT p.category,
                   SUM(oi.quantity * oi.unit_price) as revenue,
                   SUM(oi.quantity) as units
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            JOIN products p ON p.id = oi.product_id
            WHERE o.order_date >= :s AND o.order_date <= :e AND o.status != 'returned'
            GROUP BY p.category ORDER BY revenue DESC
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).fetchall()
    return [{"category": r[0], "revenue": round(r[1], 2), "units": r[2]} for r in rows]


@router.get("/slow-moving")
def get_slow_moving(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT p.id, p.name, p.category, p.stock_quantity,
                   MAX(o.order_date) as last_sale_date
            FROM products p
            LEFT JOIN order_items oi ON oi.product_id = p.id
            LEFT JOIN orders o ON o.id = oi.order_id
              AND o.order_date >= :s AND o.order_date <= :e
              AND o.status != 'returned'
            GROUP BY p.id
            HAVING COUNT(oi.id) = 0
            ORDER BY p.name
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).fetchall()
    return [
        {
            "id": r[0], "name": r[1], "category": r[2],
            "stock_quantity": r[3], "last_sale_date": r[4],
        }
        for r in rows
    ]


@router.get("/price-distribution")
def get_price_distribution(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT oi.unit_price
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.order_date >= :s AND o.order_date <= :e AND o.status != 'returned'
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).fetchall()

    buckets = {"0-50": 0, "50-100": 0, "100-200": 0, "200-300": 0, "300-500": 0, "500+": 0}
    for (price,) in rows:
        if price < 50:
            buckets["0-50"] += 1
        elif price < 100:
            buckets["50-100"] += 1
        elif price < 200:
            buckets["100-200"] += 1
        elif price < 300:
            buckets["200-300"] += 1
        elif price < 500:
            buckets["300-500"] += 1
        else:
            buckets["500+"] += 1

    return [{"range": k, "count": v} for k, v in buckets.items()]
