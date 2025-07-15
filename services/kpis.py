from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import update, delete,and_
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
