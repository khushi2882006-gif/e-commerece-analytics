from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional
from datetime import datetime, timedelta
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/customers", tags=["customers"])


def parse_dates(start_date, end_date):
    now = datetime.utcnow()
    start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else now - timedelta(days=30)
    end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else now
    end = end.replace(hour=23, minute=59, second=59)
    return start, end


@router.get("/kpis")
def get_customer_kpis(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)

    total = db.execute(text("SELECT COUNT(*) FROM customers")).scalar() or 0
    new_customers = db.execute(
        text("SELECT COUNT(*) FROM customers WHERE created_at >= :s AND created_at <= :e"),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).scalar() or 0
    returning = total - new_customers

    # avg CLV = total revenue per customer (all time)
    avg_clv = db.execute(
        text("""
            SELECT AVG(total_spend) FROM (
                SELECT customer_id, SUM(total_amount) as total_spend
                FROM orders WHERE status != 'returned'
                GROUP BY customer_id
            )
        """)
    ).scalar() or 0

    return {
        "total_customers": total,
        "new_customers": new_customers,
        "returning_customers": returning,
        "avg_clv": round(avg_clv, 2),
    }


@router.get("/acquisition")
def get_acquisition(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as new_customers
            FROM customers
            WHERE created_at >= :s AND created_at <= :e
            GROUP BY month ORDER BY month
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).fetchall()
    return [{"month": r[0], "new_customers": r[1]} for r in rows]


@router.get("/by-tier")
def get_by_tier(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    rows = db.execute(
        text("""
            SELECT c.tier, COUNT(DISTINCT c.id) as customer_count,
                   COALESCE(SUM(o.total_amount), 0) as revenue
            FROM customers c
            LEFT JOIN orders o ON o.customer_id = c.id AND o.status != 'returned'
            GROUP BY c.tier
        """)
    ).fetchall()
    return [{"tier": r[0], "customer_count": r[1], "revenue": round(r[2], 2)} for r in rows]


@router.get("/by-geography")
def get_by_geography(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT c.country, COUNT(DISTINCT o.id) as orders,
                   COALESCE(SUM(o.total_amount), 0) as revenue
            FROM customers c
            JOIN orders o ON o.customer_id = c.id
            WHERE o.order_date >= :s AND o.order_date <= :e
              AND o.status != 'returned'
            GROUP BY c.country
            ORDER BY revenue DESC
            LIMIT 20
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).fetchall()
    return [{"country": r[0], "orders": r[1], "revenue": round(r[2], 2)} for r in rows]


@router.get("/cohort-retention")
def get_cohort_retention(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    # For each customer, get their first order month and subsequent order months
    rows = db.execute(
        text("""
            WITH first_orders AS (
                SELECT customer_id,
                       strftime('%Y-%m', MIN(order_date)) as cohort_month
                FROM orders WHERE status != 'returned'
                GROUP BY customer_id
            ),
            all_orders AS (
                SELECT o.customer_id,
                       fo.cohort_month,
                       strftime('%Y-%m', o.order_date) as order_month
                FROM orders o
                JOIN first_orders fo ON fo.customer_id = o.customer_id
                WHERE o.status != 'returned'
            )
            SELECT cohort_month, order_month, COUNT(DISTINCT customer_id) as customers
            FROM all_orders
            GROUP BY cohort_month, order_month
            ORDER BY cohort_month, order_month
        """)
    ).fetchall()

    # Build cohort matrix
    from collections import defaultdict
    cohort_data = defaultdict(dict)
    cohort_sizes = {}
    for row in rows:
        cohort_month, order_month, count = row[0], row[1], row[2]
        cohort_data[cohort_month][order_month] = count
        if cohort_month == order_month:
            cohort_sizes[cohort_month] = count

    cohorts = sorted(cohort_data.keys())[-12:]  # last 12 cohorts
    all_months = sorted(set(m for c in cohort_data.values() for m in c.keys()))

    result = []
    for cohort in cohorts:
        size = cohort_sizes.get(cohort, 1)
        months_data = []
        for m in all_months:
            if m >= cohort:
                cnt = cohort_data[cohort].get(m, 0)
                months_data.append(round(cnt / size * 100, 1) if size > 0 else 0)
        result.append({"cohort_month": cohort, "cohort_size": size, "retention": months_data})

    return {"cohorts": result, "months": [m for m in all_months if m >= cohorts[0]] if cohorts else []}
