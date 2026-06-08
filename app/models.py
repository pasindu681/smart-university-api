from sqlalchemy import Column, Integer, String, Date, Time
from .database import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    resource_name = Column(String(100))
    resource_type = Column(String(50))
    capacity = Column(Integer)
    status = Column(String(20))


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer)
    resource_id = Column(Integer)

    booking_date = Column(Date)

    start_time = Column(Time)
    end_time = Column(Time)

    status = Column(String(20))