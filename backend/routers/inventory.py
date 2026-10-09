from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


def parse_dates(start_date, end_date):
    now = datetime.utcnow()
    start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else now - timedelta(days=30)
    end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else now
    end = end.replace(hour=23, minute=59, second=59)
    return start, end


@router.get("/kpis")
def get_inventory_kpis(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    total_skus = db.execute(text("SELECT COUNT(*) FROM products")).scalar() or 0
    out_of_stock = db.execute(
        text("SELECT COUNT(*) FROM products WHERE stock_quantity = 0")
    ).scalar() or 0

    # Inventory turnover = units sold / avg stock (approximate)
    turnover = db.execute(
        text("""
            SELECT AVG(turnover) FROM (
                SELECT p.id,
                       COALESCE(SUM(CASE WHEN ie.event_type='sale' THEN ABS(ie.quantity_change) ELSE 0 END), 0) * 1.0
                       / NULLIF(p.stock_quantity, 0) as turnover
                FROM products p
                LEFT JOIN inventory_events ie ON ie.product_id = p.id
                GROUP BY p.id
            )
        """)
    ).scalar() or 0

    # DIO = 365 / turnover
    dio = round(365 / turnover, 1) if turnover > 0 else 0

    return {
        "total_skus": total_skus,
        "out_of_stock_count": out_of_stock,
        "avg_turnover_ratio": round(turnover, 2),
        "avg_dio": dio,
    }


@router.get("/stock-levels")
def get_stock_levels(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    rows = db.execute(
        text("""
            SELECT category, SUM(stock_quantity) as total_stock, COUNT(*) as sku_count
            FROM products GROUP BY category ORDER BY total_stock DESC
        """)
    ).fetchall()
    return [{"category": r[0], "total_stock": r[1], "sku_count": r[2]} for r in rows]


@router.get("/turnover")
def get_turnover(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    rows = db.execute(
        text("""
            SELECT p.name, p.category,
                   COALESCE(SUM(CASE WHEN ie.event_type='sale' THEN ABS(ie.quantity_change) ELSE 0 END), 0) as units_sold,
                   p.stock_quantity,
                   CASE WHEN p.stock_quantity > 0
                        THEN ROUND(COALESCE(SUM(CASE WHEN ie.event_type='sale' THEN ABS(ie.quantity_change) ELSE 0 END), 0) * 1.0 / p.stock_quantity, 2)
                        ELSE 0
                   END as turnover_ratio
            FROM products p
            LEFT JOIN inventory_events ie ON ie.product_id = p.id
            GROUP BY p.id
            ORDER BY turnover_ratio DESC
            LIMIT 20
        """)
    ).fetchall()
    return [
        {"name": r[0], "category": r[1], "units_sold": r[2], "stock_quantity": r[3], "turnover_ratio": r[4]}
        for r in rows
    ]


@router.get("/stockout-events")
def get_stockout_events(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    rows = db.execute(
        text("""
            SELECT p.name, p.category, p.stock_quantity,
                   MIN(ie.event_date) as first_stockout
            FROM products p
            JOIN inventory_events ie ON ie.product_id = p.id AND ie.event_type = 'sale'
            WHERE p.stock_quantity <= 5
            GROUP BY p.id
            ORDER BY p.stock_quantity ASC
            LIMIT 20
        """)
    ).fetchall()
    return [{"name": r[0], "category": r[1], "stock_quantity": r[2], "first_stockout": str(r[3]) if r[3] else None} for r in rows]


@router.get("/restock-timeline")
def get_restock_timeline(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT strftime('%Y-%m', event_date) as month,
                   SUM(quantity_change) as total_restocked,
                   COUNT(*) as restock_events
            FROM inventory_events
            WHERE event_type = 'restock'
              AND event_date >= :s AND event_date <= :e
            GROUP BY month ORDER BY month
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).fetchall()
    return [{"month": r[0], "total_restocked": r[1], "restock_events": r[2]} for r in rows]
