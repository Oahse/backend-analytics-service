from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import update, delete,and_,text
from uuid import UUID
from core.utils.generator import generator
from schemas.orders import OrderSchema, OrderItemSchema,UpdateOrderSchema,OrderFilterSchema
from core.config import settings
from core.utils.kafka import KafkaProducer, send_kafka_message, is_kafka_available
from datetime import datetime
from datetime import date

from models.kpis import DailyKPIs, OrderEvents  # Adjust import path as needed


kafka_producer = KafkaProducer(broker=settings.KAFKA_BOOTSTRAP_SERVERS,
                                topic=str(settings.KAFKA_TOPIC))

class KPIService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily_kpis(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[DailyKPIs]:
        stmt = select(DailyKPIs)
        if start_date:
            stmt = stmt.where(DailyKPIs.date >= start_date)
        if end_date:
            stmt = stmt.where(DailyKPIs.date <= end_date)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_kpi_by_date(self, target_date: date) -> Optional[DailyKPIs]:
        stmt = select(DailyKPIs).where(DailyKPIs.date == target_date)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_weekly_kpis(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT toStartOfWeek(date) AS week_start,
                   sum(total_orders) AS total_orders,
                   sum(total_revenue) AS total_revenue,
                   sum(total_customers) AS total_customers,
                   sum(total_earnings) AS total_earnings
            FROM daily_kpis
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

    async def get_monthly_kpis(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT toStartOfMonth(date) AS month_start,
                   sum(total_orders) AS total_orders,
                   sum(total_revenue) AS total_revenue,
                   sum(total_customers) AS total_customers,
                   sum(total_earnings) AS total_earnings
            FROM daily_kpis
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

    async def get_yearly_kpis(self) -> List[Dict[str, Any]]:
        sql = """
            SELECT toStartOfYear(date) AS year_start,
                   sum(total_orders) AS total_orders,
                   sum(total_revenue) AS total_revenue,
                   sum(total_customers) AS total_customers,
                   sum(total_earnings) AS total_earnings
            FROM daily_kpis
            GROUP BY year_start
            ORDER BY year_start
        """
        result = await self.db.execute(text(sql))
        return [dict(row) for row in result.all()]