from fastapi import APIRouter, Request, Form, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import shutil
from database import get_db
from models import User

router = APIRouter(prefix="/portal")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "static/uploads/certs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_class=HTMLResponse)
async def talent_portal(request: Request):
    return templates.TemplateResponse("portal/signup.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def freelancer_dashboard(request: Request):
    return templates.TemplateResponse("portal/dashboard.html", {"request": request})

@router.post("/signup")
async def register_freelancer(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    gender: str = Form(...),
    whatsapp: str = Form(...),
    primary_skill: str = Form(...),
    custom_skill: str = Form(None),
    bank_details: str = Form(None),
    certifications: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    cert_path = None
    if certifications and certifications.filename:
        cert_path = os.path.join(UPLOAD_DIR, f"{email}_{certifications.filename}")
        with open(cert_path, "wb") as buffer:
            shutil.copyfileobj(certifications.file, buffer)
    
    new_user = User(
        name=name,
        email=email,
        role="freelancer",
        gender=gender,
        whatsapp=whatsapp,
        primary_skill=primary_skill,
        custom_skill=custom_skill if primary_skill == "Other / Custom" else None,
        bank_details=bank_details,
        certifications_path=cert_path
    )
    
    db.add(new_user)
    db.commit()
    
    return templates.TemplateResponse("portal/signup_success.html", {"request": request, "name": name})
