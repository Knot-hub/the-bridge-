from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import Lead, Message

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("storefront/index.html", {"request": request})

@router.get("/explore", response_class=HTMLResponse)
async def explore_services(request: Request):
    return templates.TemplateResponse("storefront/explore.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def client_dashboard(request: Request):
    return templates.TemplateResponse("storefront/dashboard.html", {"request": request})

@router.post("/send-message")
async def send_message(
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    new_msg = Message(
        sender_email=email,
        subject=subject,
        content=message
    )
    db.add(new_msg)
    db.commit()
    return RedirectResponse(url="/dashboard?sent=true", status_code=303)

@router.get("/request-service", response_class=HTMLResponse)
async def request_service_page(request: Request):
    return templates.TemplateResponse("storefront/request_service.html", {"request": request})

@router.get("/invite", response_class=HTMLResponse)
async def invitation_page(request: Request):
    return templates.TemplateResponse("invitation.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("storefront/login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("storefront/register.html", {"request": request})

@router.get("/status-check", response_class=HTMLResponse)
async def status_check_page(request: Request):
    return templates.TemplateResponse("storefront/status_check.html", {"request": request})

@router.post("/status-check", response_class=HTMLResponse)
async def check_status(request: Request, email: str = Form(...), db: Session = Depends(get_db)):
    # Look up leads by client_contact (which stores email in this mock)
    leads = db.query(Lead).filter(Lead.client_contact == email).all()
    return templates.TemplateResponse("storefront/status_check.html", {
        "request": request, 
        "leads": leads, 
        "email": email
    })
