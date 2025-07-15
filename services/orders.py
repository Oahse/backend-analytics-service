from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from typing import List, Optional

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
