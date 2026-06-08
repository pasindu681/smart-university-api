from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date, time
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form
from fastapi.responses import RedirectResponse



from .database import engine, SessionLocal
from .models import Base, Resource, Booking

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart University Resource Booking API"
)
templates = Jinja2Templates(directory="templates")


# -------------------------
# Request Model
# -------------------------

class BookingRequest(BaseModel):
    user_id: int
    resource_id: int
    booking_date: date
    start_time: time
    end_time: time


# -------------------------
# Root
# -------------------------

@app.get("/")
def root():
    return {
        "message": "API Running Successfully"
    }


# -------------------------
# Get Resources
# -------------------------

@app.get("/resources")
def get_resources():

    db: Session = SessionLocal()

    return db.query(Resource).all()


# -------------------------
# Create Booking
# -------------------------

@app.post("/bookings")
def create_booking(request: BookingRequest):

    db = SessionLocal()

    existing = db.query(Booking).filter(
        Booking.resource_id == request.resource_id,
        Booking.booking_date == request.booking_date,
        Booking.start_time == request.start_time,
        Booking.end_time == request.end_time
    ).first()

    if existing:
        return {
            "message": "Resource already booked for this time slot"
        }

    booking = Booking(
        user_id=request.user_id,
        resource_id=request.resource_id,
        booking_date=request.booking_date,
        start_time=request.start_time,
        end_time=request.end_time,
        status="pending"
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return {
        "message": "Booking Created Successfully",
        "booking_id": booking.id
    }


# -------------------------
# View All Bookings
# -------------------------

@app.get("/bookings")
def get_bookings():

    db = SessionLocal()

    return db.query(Booking).all()


# -------------------------
# Approve Booking
# -------------------------

@app.put("/bookings/{booking_id}/approve")
def approve_booking(booking_id: int):

    db = SessionLocal()

    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    booking.status = "approved"

    db.commit()

    return {
        "message": "Booking Approved Successfully"
    }


# -------------------------
# Reject Booking
# -------------------------

@app.put("/bookings/{booking_id}/reject")
def reject_booking(booking_id: int):

    db = SessionLocal()

    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    booking.status = "rejected"

    db.commit()

    return {
        "message": "Booking Rejected Successfully"
    }

# -------------------------
# Cancel Booking
# -------------------------

@app.put("/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int):

    db = SessionLocal()

    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    booking.status = "cancelled"

    db.commit()

    return {
        "message": "Booking Cancelled Successfully"
    }


# -------------------------
# Get Single Booking
# -------------------------

@app.get("/bookings/{booking_id}")
def get_booking(booking_id: int):

    db = SessionLocal()

    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return booking


# -------------------------
# Delete Booking
# -------------------------

@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int):

    db = SessionLocal()

    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    db.delete(booking)
    db.commit()

    return {
        "message": "Booking Deleted Successfully"
    }
# -------------------------
# Dashboard
# -------------------------

@app.get("/dashboard")
def dashboard():

    db = SessionLocal()

    total_resources = db.query(Resource).count()
    total_bookings = db.query(Booking).count()

    pending = db.query(Booking).filter(
        Booking.status == "pending"
    ).count()

    approved = db.query(Booking).filter(
        Booking.status == "approved"
    ).count()

    rejected = db.query(Booking).filter(
        Booking.status == "rejected"
    ).count()

    cancelled = db.query(Booking).filter(
        Booking.status == "cancelled"
    ).count()

    return {
        "total_resources": total_resources,
        "total_bookings": total_bookings,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "cancelled": cancelled
    }


# -------------------------
# Resource Availability
# -------------------------

@app.get("/availability/{resource_id}")
def check_availability(resource_id: int):

    db = SessionLocal()

    resource = db.query(Resource).filter(
        Resource.id == resource_id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    active_booking = db.query(Booking).filter(
        Booking.resource_id == resource_id,
        Booking.status.in_(["pending", "approved"])
    ).first()

    return {
        "resource_id": resource_id,
        "resource_name": resource.resource_name,
        "available": active_booking is None
    }
@app.get("/home", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )




@app.get("/resources-page", response_class=HTMLResponse)
def resources_page(request: Request):

    db = SessionLocal()

    resources = db.query(Resource).all()

    print(resources)

    return templates.TemplateResponse(
        request=request,
        name="resources.html",
        context={
            "resources": resources
        }
    )

@app.get("/bookings-page", response_class=HTMLResponse)
def bookings_page(request: Request):

    db = SessionLocal()

    bookings = db.query(Booking).all()

    return templates.TemplateResponse(
        request=request,
        name="bookings.html",
        context={
            "bookings": bookings
        }
    )
@app.post("/create-booking")
def create_booking_web(

    user_id: int = Form(...),
    resource_id: int = Form(...),
    booking_date: date = Form(...),
    start_time: time = Form(...),
    end_time: time = Form(...)

):

    db = SessionLocal()

    booking = Booking(

        user_id=user_id,
        resource_id=resource_id,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        status="pending"

    )

    db.add(booking)
    db.commit()

    return RedirectResponse(
        url="/bookings-page",
        status_code=303
    )

@app.get("/approve-booking/{booking_id}")
def approve_booking_web(booking_id: int):

    db = SessionLocal()

    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if booking:
        booking.status = "approved"
        db.commit()

    return RedirectResponse(
        url="/bookings-page",
        status_code=303
    )

@app.get("/reject-booking/{booking_id}")
def reject_booking_web(booking_id: int):

    db = SessionLocal()

    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if booking:
        booking.status = "rejected"
        db.commit()

    return RedirectResponse(
        url="/bookings-page",
        status_code=303
    )

@app.get("/cancel-booking/{booking_id}")
def cancel_booking_web(booking_id: int):

    db = SessionLocal()

    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if booking:
        booking.status = "cancelled"
        db.commit()

    return RedirectResponse(
        url="/bookings-page",
        status_code=303
    )

@app.get("/delete-booking/{booking_id}")
def delete_booking_web(booking_id: int):

    db = SessionLocal()

    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if booking:
        db.delete(booking)
        db.commit()

    return RedirectResponse(
        url="/bookings-page",
        status_code=303
    )

@app.get("/dashboard-page", response_class=HTMLResponse)
def dashboard_page(request: Request):

    db = SessionLocal()

    total_resources = db.query(Resource).count()
    total_bookings = db.query(Booking).count()

    pending = db.query(Booking).filter(
        Booking.status == "pending"
    ).count()

    approved = db.query(Booking).filter(
        Booking.status == "approved"
    ).count()

    rejected = db.query(Booking).filter(
        Booking.status == "rejected"
    ).count()

    cancelled = db.query(Booking).filter(
        Booking.status == "cancelled"
    ).count()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "total_resources": total_resources,
            "total_bookings": total_bookings,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "cancelled": cancelled
        }
    )
@app.get("/bookings-page", response_class=HTMLResponse)
def bookings_page(request: Request):

    db = SessionLocal()

    bookings = db.query(Booking).all()
    resources = db.query(Resource).all()

    return templates.TemplateResponse(
        request=request,
        name="bookings.html",
        context={
            "bookings": bookings,
            "resources": resources
        }
    )

#tempory data add db

@app.on_event("startup")
def seed_data():

    db = SessionLocal()

    # Seed Resources
    if db.query(Resource).count() == 0:

        resources = [
            Resource(
                resource_name="Lecture Hall A",
                resource_type="lecture_hall",
                capacity=150,
                status="available"
            ),
            Resource(
                resource_name="Lecture Hall B",
                resource_type="lecture_hall",
                capacity=120,
                status="available"
            ),
            Resource(
                resource_name="Computer Lab 01",
                resource_type="computer_lab",
                capacity=40,
                status="available"
            ),
            Resource(
                resource_name="Computer Lab 02",
                resource_type="computer_lab",
                capacity=35,
                status="available"
            ),
            Resource(
                resource_name="Meeting Room 01",
                resource_type="meeting_room",
                capacity=20,
                status="available"
            ),
            Resource(
                resource_name="Projector 01",
                resource_type="projector",
                capacity=1,
                status="available"
            ),
            Resource(
                resource_name="Basketball Court",
                resource_type="sports_facility",
                capacity=50,
                status="available"
            )
        ]

        db.add_all(resources)
        db.commit()

    # Seed Sample Booking
    if db.query(Booking).count() == 0:

        booking = Booking(
            user_id=1,
            resource_id=1,
            booking_date=date.today(),
            start_time=time(9, 0),
            end_time=time(11, 0),
            status="approved"
        )

        db.add(booking)
        db.commit()

    db.close()

