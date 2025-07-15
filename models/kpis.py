from sqlalchemy import Column
from clickhouse_sqlalchemy import types, engines
from core.database import Base


class DailyKPIs(Base):
    __tablename__ = "daily_kpis"
    __table_args__ = (
        engines.MergeTree(
            partition_by=types.Date,
            order_by=["date"]
        ),
    )

    date = Column(types.Date, primary_key=True)
    total_orders = Column(types.UInt32)
    total_revenue = Column(types.Float64)
    total_customers = Column(types.UInt32)
    total_earnings = Column(types.Float64)

    def to_dict(self):
        return {
            "date": str(self.date),
            "total_orders": self.total_orders,
            "total_revenue": self.total_revenue,
            "total_customers": self.total_customers,
            "total_earnings": self.total_earnings,
        }

    def __repr__(self):
        return (
            f"<DailyKPIs(date={self.date}, orders={self.total_orders}, "
            f"revenue={self.total_revenue}, customers={self.total_customers}, "
            f"earnings={self.total_earnings})>"
        )


class OrderEvents(Base):
    __tablename__ = "order_events"
    __table_args__ = (
        engines.SummingMergeTree(
            partition_by=types.Date,
            order_by=["date"]
        ),
    )

    date = Column(types.Date, primary_key=True)
    total_orders = Column(types.UInt32)
    total_revenue = Column(types.Float64)
    total_earnings = Column(types.Float64)

    def to_dict(self):
        return {
            "date": str(self.date),
            "total_orders": self.total_orders,
            "total_revenue": self.total_revenue,
            "total_earnings": self.total_earnings,
        }

    def __repr__(self):
        return (
            f"<OrderEvents(date={self.date}, orders={self.total_orders}, "
            f"revenue={self.total_revenue}, earnings={self.total_earnings})>"
        )
