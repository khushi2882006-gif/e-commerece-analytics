from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional
from datetime import datetime, date, timedelta
from database import get_db
from auth import get_current_user
from models.order import Order, OrderItem
from models.product import Product

router = APIRouter(prefix="/api/sales", tags=["sales"])

MONTHLY_TARGET = 50000.0


def parse_dates(start_date: Optional[str], end_date: Optional[str]):
    now = datetime.utcnow()
    start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else now - timedelta(days=30)
    end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else now
    # set end to end of day
    end = end.replace(hour=23, minute=59, second=59)
    return start, end


@router.get("/kpis")
def get_sales_kpis(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)

    def period_stats(s, e):
        result = db.query(
            func.coalesce(func.sum(Order.total_amount), 0).label("revenue"),
            func.count(Order.id).label("orders"),
        ).filter(Order.order_date >= s, Order.order_date <= e, Order.status != "returned").first()
        return result.revenue, result.orders

    revenue, orders = period_stats(start, end)
    aov = round(revenue / orders, 2) if orders > 0 else 0

    # MoM: previous same-length period
    delta = end - start
    prev_start = start - delta - timedelta(days=1)
    prev_end = start - timedelta(days=1)
    prev_revenue, prev_orders = period_stats(prev_start, prev_end)

    mom_change = round(((revenue - prev_revenue) / prev_revenue * 100), 1) if prev_revenue > 0 else 0

    # YoY
    yoy_start = start - timedelta(days=365)
    yoy_end = end - timedelta(days=365)
    yoy_revenue, _ = period_stats(yoy_start, yoy_end)
    yoy_change = round(((revenue - yoy_revenue) / yoy_revenue * 100), 1) if yoy_revenue > 0 else 0

    # Refund rate
    total_all = db.query(func.count(Order.id)).filter(
        Order.order_date >= start, Order.order_date <= end
    ).scalar() or 0
    returned = db.query(func.count(Order.id)).filter(
        Order.order_date >= start, Order.order_date <= end, Order.status == "returned"
    ).scalar() or 0
    refund_rate = round((returned / total_all * 100), 1) if total_all > 0 else 0

    return {
        "total_revenue": round(revenue, 2),
        "total_orders": orders,
        "aov": aov,
        "refund_rate": refund_rate,
        "mom_change": mom_change,
        "yoy_change": yoy_change,
    }


@router.get("/trend")
def get_sales_trend(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    period: str = Query("day", regex="^(day|week|month)$"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)

    fmt_map = {"day": "%Y-%m-%d", "week": "%Y-%W", "month": "%Y-%m"}
    fmt = fmt_map[period]

    rows = db.execute(
        text("""
            SELECT strftime(:fmt, order_date) as period,
                   SUM(total_amount) as revenue,
                   COUNT(id) as orders
            FROM orders
            WHERE order_date >= :start AND order_date <= :end
              AND status != 'returned'
            GROUP BY period
            ORDER BY period
        """),
        {"fmt": fmt, "start": start.isoformat(), "end": end.isoformat()},
    ).fetchall()

    return [{"period": r[0], "revenue": round(r[1], 2), "orders": r[2]} for r in rows]


@router.get("/by-channel")
def get_sales_by_channel(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT channel,
                   SUM(total_amount) as revenue,
                   COUNT(id) as orders
            FROM orders
            WHERE order_date >= :start AND order_date <= :end
              AND status != 'returned'
            GROUP BY channel
        """),
        {"start": start.isoformat(), "end": end.isoformat()},
    ).fetchall()
    return [{"channel": r[0], "revenue": round(r[1], 2), "orders": r[2]} for r in rows]


@router.get("/revenue-vs-target")
def get_revenue_vs_target(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT strftime('%Y-%m', order_date) as month,
                   SUM(total_amount) as revenue
            FROM orders
            WHERE order_date >= :start AND order_date <= :end
              AND status != 'returned'
            GROUP BY month
            ORDER BY month
        """),
        {"start": start.isoformat(), "end": end.isoformat()},
    ).fetchall()
    return [{"month": r[0], "revenue": round(r[1], 2), "target": MONTHLY_TARGET} for r in rows]
