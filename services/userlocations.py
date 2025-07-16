from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import date
from models.kpis import OrderEvents
from schemas.kpis import OrderEventsSchema  # Your schema with constr, confloat etc.

class OrderEventService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_order_events(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[OrderEventsSchema]:
        stmt = select(OrderEvents)
        if start_date:
            stmt = stmt.where(OrderEvents.date >= start_date)
        if end_date:
            stmt = stmt.where(OrderEvents.date <= end_date)

        result = await self.db.execute(stmt)
        records = result.scalars().all()
        return [OrderEventsSchema.from_orm(rec) for rec in records]

    async def get_order_event_by_date(self, target_date: date) -> Optional[OrderEventsSchema]:
        stmt = select(OrderEvents).where(OrderEvents.date == target_date)
        result = await self.db.execute(stmt)
        record = result.scalar_one_or_none()
        return OrderEventsSchema.from_orm(record) if record else None

    async def get_weekly_order_events(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        stmt = (
            select(
                func.date_trunc('week', OrderEvents.date).label('week_start'),
                func.sum(OrderEvents.total_orders).label('total_orders'),
                func.sum(OrderEvents.total_revenue).label('total_revenue'),
                func.sum(OrderEvents.total_earnings).label('total_earnings'),
            )
            .group_by('week_start')
            .order_by('week_start')
        )
        if year:
            stmt = stmt.where(func.extract('year', OrderEvents.date) == year)

        result = await self.db.execute(stmt)
        return [dict(row) for row in result.all()]

    async def get_monthly_order_events(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        stmt = (
            select(
                func.date_trunc('month', OrderEvents.date).label('month_start'),
                func.sum(OrderEvents.total_orders).label('total_orders'),
                func.sum(OrderEvents.total_revenue).label('total_revenue'),
                func.sum(OrderEvents.total_earnings).label('total_earnings'),
            )
            .group_by('month_start')
            .order_by('month_start')
        )
        if year:
            stmt = stmt.where(func.extract('year', OrderEvents.date) == year)

        result = await self.db.execute(stmt)
        return [dict(row) for row in result.all()]

    async def get_yearly_order_events(self) -> List[Dict[str, Any]]:
        stmt = (
            select(
                func.date_trunc('year', OrderEvents.date).label('year_start'),
                func.sum(OrderEvents.total_orders).label('total_orders'),
                func.sum(OrderEvents.total_revenue).label('total_revenue'),
                func.sum(OrderEvents.total_earnings).label('total_earnings'),
            )
            .group_by('year_start')
            .order_by('year_start')
        )
        result = await self.db.execute(stmt)
        return [dict(row) for row in result.all()]
    
    async def add_or_update(self, data: OrderEventsSchema) -> OrderEventsSchema:
        # Try to find existing record by date
        stmt = select(OrderEvents).where(OrderEvents.date == data.date)
        result = await self.db.execute(stmt)
        existing_record = result.scalar_one_or_none()

        if existing_record:
            # Update existing record
            existing_record.total_orders = data.total_orders
            existing_record.total_revenue = data.total_revenue
            existing_record.total_earnings = data.total_earnings
            self.db.add(existing_record)  # Optional if already in session
            await self.db.commit()
            await self.db.refresh(existing_record)
            return OrderEventsSchema.from_orm(existing_record)

        # Insert new record
        new_record = OrderEvents(
            date=data.date,
            total_orders=data.total_orders,
            total_revenue=data.total_revenue,
            total_earnings=data.total_earnings,
        )
        self.db.add(new_record)
        await self.db.commit()
        await self.db.refresh(new_record)
        return OrderEventsSchema.from_orm(new_record)