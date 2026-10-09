from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/marketing", tags=["marketing"])


def parse_dates(start_date, end_date):
    now = datetime.utcnow()
    start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else now - timedelta(days=30)
    end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else now
    end = end.replace(hour=23, minute=59, second=59)
    return start, end


@router.get("/kpis")
def get_marketing_kpis(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)

    total_spend = db.execute(
        text("""
            SELECT COALESCE(SUM(spend_amount), 0) FROM marketing_spend
            WHERE period_date >= :s AND period_date <= :e
        """),
        {"s": start.date().isoformat(), "e": end.date().isoformat()},
    ).scalar() or 0

    promo_revenue = db.execute(
        text("""
            SELECT COALESCE(SUM(total_amount), 0) FROM orders
            WHERE promo_code IS NOT NULL AND order_date >= :s AND order_date <= :e
              AND status != 'returned'
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).scalar() or 0

    total_revenue = db.execute(
        text("""
            SELECT COALESCE(SUM(total_amount), 0) FROM orders
            WHERE order_date >= :s AND order_date <= :e AND status != 'returned'
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).scalar() or 0

    new_customers = db.execute(
        text("SELECT COUNT(*) FROM customers WHERE created_at >= :s AND created_at <= :e"),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).scalar() or 0

    roas = round(total_revenue / total_spend, 2) if total_spend > 0 else 0
    cpa = round(total_spend / new_customers, 2) if new_customers > 0 else 0

    return {
        "total_spend": round(total_spend, 2),
        "promo_revenue": round(promo_revenue, 2),
        "roas": roas,
        "cpa": cpa,
    }


@router.get("/promo-impact")
def get_promo_impact(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT promo_code, COUNT(*) as orders,
                   SUM(total_amount) as revenue,
                   SUM(discount_amount) as total_discount
            FROM orders
            WHERE promo_code IS NOT NULL
              AND order_date >= :s AND order_date <= :e
              AND status != 'returned'
            GROUP BY promo_code ORDER BY revenue DESC
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).fetchall()
    return [
        {"promo_code": r[0], "orders": r[1], "revenue": round(r[2], 2), "total_discount": round(r[3], 2)}
        for r in rows
    ]


@router.get("/channel-conversion")
def get_channel_conversion(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT channel, COUNT(*) as orders,
                   SUM(CASE WHEN status='returned' THEN 1 ELSE 0 END) as returns
            FROM orders
            WHERE order_date >= :s AND order_date <= :e
            GROUP BY channel
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).fetchall()
    return [
        {"channel": r[0], "orders": r[1], "returns": r[2]}
        for r in rows
    ]


@router.get("/spend-vs-revenue")
def get_spend_vs_revenue(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)

    spend_rows = db.execute(
        text("""
            SELECT strftime('%Y-%m', period_date) as month, SUM(spend_amount) as spend
            FROM marketing_spend
            WHERE period_date >= :s AND period_date <= :e
            GROUP BY month ORDER BY month
        """),
        {"s": start.date().isoformat(), "e": end.date().isoformat()},
    ).fetchall()

    revenue_rows = db.execute(
        text("""
            SELECT strftime('%Y-%m', order_date) as month, SUM(total_amount) as revenue
            FROM orders
            WHERE order_date >= :s AND order_date <= :e AND status != 'returned'
            GROUP BY month ORDER BY month
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).fetchall()

    spend_map = {r[0]: round(r[1], 2) for r in spend_rows}
    revenue_map = {r[0]: round(r[1], 2) for r in revenue_rows}
    all_months = sorted(set(list(spend_map.keys()) + list(revenue_map.keys())))

    return [
        {"month": m, "spend": spend_map.get(m, 0), "revenue": revenue_map.get(m, 0)}
        for m in all_months
    ]
