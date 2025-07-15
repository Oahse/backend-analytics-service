from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete,func, text
from datetime import datetime, date

from models.kpis import OrderEvents  # Adjust path


class OrderEventService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_order_events(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[OrderEvents]:
        stmt = select(OrderEvents)
        if start_date:
            stmt = stmt.where(OrderEvents.date >= start_date)
        if end_date:
            stmt = stmt.where(OrderEvents.date <= end_date)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_order_event_by_date(self, target_date: date) -> Optional[OrderEvents]:
        stmt = select(OrderEvents).where(OrderEvents.date == target_date)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_weekly_order_events(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        # Aggregate by week start date
        sql = """
            SELECT toStartOfWeek(date) AS week_start,
                   sum(total_orders) AS total_orders,
                   sum(total_revenue) AS total_revenue,
                   sum(total_earnings) AS total_earnings
            FROM order_events
            {where_clause}
            GROUP BY week_start
            ORDER BY week_start
        """

        where_clause = ""
        params = {}

        if year:
            where_clause = "WHERE toYear(date) = :year"
            params["year"] = year

        sql = sql.format(where_clause=where_clause)

        result = await self.db.execute(text(sql).bindparams(**params))
        return [dict(row) for row in result.all()]

    async def get_monthly_order_events(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT toStartOfMonth(date) AS month_start,
                   sum(total_orders) AS total_orders,
                   sum(total_revenue) AS total_revenue,
                   sum(total_earnings) AS total_earnings
            FROM order_events
            {where_clause}
            GROUP BY month_start
            ORDER BY month_start
        """
        where_clause = ""
        params = {}

        if year:
            where_clause = "WHERE toYear(date) = :year"
            params["year"] = year

        sql = sql.format(where_clause=where_clause)

        result = await self.db.execute(text(sql).bindparams(**params))
        return [dict(row) for row in result.all()]

    async def get_yearly_order_events(self) -> List[Dict[str, Any]]:
        sql = """
            SELECT toStartOfYear(date) AS year_start,
                   sum(total_orders) AS total_orders,
                   sum(total_revenue) AS total_revenue,
                   sum(total_earnings) AS total_earnings
            FROM order_events
            GROUP BY year_start
            ORDER BY year_start
        """
        result = await self.db.execute(text(sql))
        return [dict(row) for row in result.all()]