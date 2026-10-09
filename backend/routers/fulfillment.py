from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/fulfillment", tags=["fulfillment"])


def parse_dates(start_date, end_date):
    now = datetime.utcnow()
    start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else now - timedelta(days=30)
    end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else now
    end = end.replace(hour=23, minute=59, second=59)
    return start, end


@router.get("/kpis")
def get_fulfillment_kpis(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)

    avg_delivery = db.execute(
        text("""
            SELECT AVG(julianday(delivered_date) - julianday(shipped_date))
            FROM shipment_events se
            JOIN orders o ON o.id = se.order_id
            WHERE se.status = 'delivered'
              AND o.order_date >= :s AND o.order_date <= :e
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).scalar() or 0

    total_shipments = db.execute(
        text("""
            SELECT COUNT(*) FROM shipment_events se
            JOIN orders o ON o.id = se.order_id
            WHERE o.order_date >= :s AND o.order_date <= :e
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).scalar() or 1

    late_count = db.execute(
        text("""
            SELECT COUNT(*) FROM shipment_events se
            JOIN orders o ON o.id = se.order_id
            WHERE se.status = 'delivered'
              AND julianday(delivered_date) - julianday(shipped_date) > 5
              AND o.order_date >= :s AND o.order_date <= :e
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).scalar() or 0

    failed_count = db.execute(
        text("""
            SELECT COUNT(*) FROM shipment_events se
            JOIN orders o ON o.id = se.order_id
            WHERE se.status = 'failed'
              AND o.order_date >= :s AND o.order_date <= :e
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).scalar() or 0

    avg_cycle = db.execute(
        text("""
            SELECT AVG(julianday(se.shipped_date) - julianday(o.order_date))
            FROM shipment_events se
            JOIN orders o ON o.id = se.order_id
            WHERE se.shipped_date IS NOT NULL
              AND o.order_date >= :s AND o.order_date <= :e
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).scalar() or 0

    return {
        "avg_delivery_days": round(avg_delivery, 1),
        "late_delivery_rate": round(late_count / total_shipments * 100, 1),
        "failed_delivery_rate": round(failed_count / total_shipments * 100, 1),
        "avg_fulfillment_cycle_days": round(avg_cycle, 1),
    }


@router.get("/by-carrier")
def get_by_carrier(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT se.carrier,
                   AVG(julianday(se.delivered_date) - julianday(se.shipped_date)) as avg_days,
                   COUNT(*) as total,
                   SUM(CASE WHEN se.status='failed' THEN 1 ELSE 0 END) as failed
            FROM shipment_events se
            JOIN orders o ON o.id = se.order_id
            WHERE se.delivered_date IS NOT NULL
              AND o.order_date >= :s AND o.order_date <= :e
            GROUP BY se.carrier ORDER BY avg_days ASC
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).fetchall()
    return [
        {
            "carrier": r[0],
            "avg_delivery_days": round(r[1], 1) if r[1] else 0,
            "total_shipments": r[2],
            "failed_count": r[3],
            "failure_rate": round(r[3] / r[2] * 100, 1) if r[2] > 0 else 0,
        }
        for r in rows
    ]


@router.get("/delivery-trend")
def get_delivery_trend(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT strftime('%Y-%m', o.order_date) as month,
                   AVG(julianday(se.delivered_date) - julianday(se.shipped_date)) as avg_days
            FROM shipment_events se
            JOIN orders o ON o.id = se.order_id
            WHERE se.status = 'delivered'
              AND o.order_date >= :s AND o.order_date <= :e
            GROUP BY month ORDER BY month
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).fetchall()
    return [{"month": r[0], "avg_delivery_days": round(r[1], 1) if r[1] else 0} for r in rows]


@router.get("/fulfillment-cycle")
def get_fulfillment_cycle(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    start, end = parse_dates(start_date, end_date)
    rows = db.execute(
        text("""
            SELECT o.id, se.carrier, o.order_date, se.shipped_date, se.status,
                   ROUND(julianday(se.shipped_date) - julianday(o.order_date), 1) as cycle_days
            FROM shipment_events se
            JOIN orders o ON o.id = se.order_id
            WHERE se.status IN ('failed', 'in-transit')
              AND o.order_date >= :s AND o.order_date <= :e
            ORDER BY o.order_date DESC
            LIMIT 50
        """),
        {"s": start.isoformat(), "e": end.isoformat()},
    ).fetchall()
    return [
        {
            "order_id": r[0], "carrier": r[1],
            "order_date": str(r[2])[:10] if r[2] else None,
            "shipped_date": str(r[3])[:10] if r[3] else None,
            "status": r[4], "cycle_days": r[5],
        }
        for r in rows
    ]
