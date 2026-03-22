from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json
from database import get_db
from models import Lead, User, ScrapedFreelancer, Task, Template, Message
from scraper import scrape_wwr_jobs, scrape_freelancers

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    # Fetch live leads from database
    leads = db.query(Lead).order_by(Lead.id.desc()).all()
    # Fetch registered freelancers for assignment
    freelancers = db.query(User).filter(User.role == "freelancer").all()
    # Fetch scraped freelancers for assignment
    scraped = db.query(ScrapedFreelancer).all()
    # Fetch outreach templates
    outreach_templates = db.query(Template).all()
    # Fetch client messages
    client_messages = db.query(Message).order_by(Message.id.desc()).all()
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request, 
        "leads": leads,
        "freelancers": freelancers,
        "scraped": scraped,
        "outreach_templates": outreach_templates,
        "client_messages": client_messages
    })


@router.post("/scrape")
async def trigger_scrape(db: Session = Depends(get_db)):
    jobs = scrape_wwr_jobs()
    new_leads_count = 0
    
    for job in jobs:
        # Deduplication: check if link already exists
        existing = db.query(Lead).filter(Lead.link == job["link"]).first()
        if not existing:
            new_lead = Lead(
                title=job.get("title", "No Title"),
                link=job.get("link", "#"),
                description=(job.get("description") or "")[:500], # Truncate safely
                source_price=100.0, # Default Estimated Budget
                client_contact="RSS Feed",
                status="new"
            )
            db.add(new_lead)
            new_leads_count += 1
    
    db.commit()
    return {"message": f"Successfully scraped. Added {new_leads_count} new leads."}

@router.get("/talent-scout", response_class=HTMLResponse)
async def talent_scout(request: Request, db: Session = Depends(get_db)):
    scraped_freelancers = db.query(ScrapedFreelancer).order_by(ScrapedFreelancer.id.desc()).all()
    return templates.TemplateResponse("admin/talent_scout.html", {"request": request, "freelancers": scraped_freelancers})

@router.post("/scout")
async def trigger_scout(keyword: str = Form(...), db: Session = Depends(get_db)):
    freelancers = scrape_freelancers(keyword)
    new_count = 0
    for f in freelancers:
        existing = db.query(ScrapedFreelancer).filter(ScrapedFreelancer.profile_link == f["link"]).first()
        if not existing:
            new_f = ScrapedFreelancer(
                name=f["name"],
                profile_link=f["link"],
                skills=f["skills"],
                source=f["source"]
            )
            db.add(new_f)
            new_count += 1
    db.commit()
    return RedirectResponse(url="/admin/talent-scout", status_code=303)

@router.post("/assign-lead")
async def assign_lead(
    lead_id: int = Form(...),
    freelancer_id: int = Form(None),
    scraped_id: int = Form(None),
    payout: float = Form(...),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Create Task
    new_task = Task(
        lead_id=lead_id,
        assigned_freelancer_id=freelancer_id,
        assigned_scraped_id=scraped_id,
        payout_price=payout,
        status="assigned"
    )
    
    lead.status = "assigned"
    db.add(new_task)
    db.commit()
    
    return RedirectResponse(url="/admin/", status_code=303)

@router.get("/finance-vault", response_class=HTMLResponse)
async def finance_vault(request: Request, db: Session = Depends(get_db)):
    # Total Revenue: Sum of source_price for 'PAID' leads
    revenue_leads = db.query(Lead).filter(Lead.status == "PAID").all()
    total_revenue = sum(l.source_price for l in revenue_leads)
    
    # Total Liabilities: Sum of payout_price for tasks where status is 'assigned' (not yet settled)
    liabilities_tasks = db.query(Task).filter(Task.status == "assigned").all()
    total_liabilities = sum(t.payout_price for t in liabilities_tasks)
    
    # Net Profit
    net_profit = total_revenue - total_liabilities
    
    # Fetch all tasks for the payout table
    tasks = db.query(Task).order_by(Task.id.desc()).all()

    # --- New Features for Finance Vault ---
    # 1. Project Distribution (by category or status)
    from sqlalchemy import func
    category_data = db.query(Lead.title, func.count(Lead.id)).group_by(Lead.title).all()
    # Note: Since Lead doesn't have a category field yet, we'll mock some data for the chart
    # based on the title keywords if possible, or just use status for now.
    status_distribution = db.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
    status_labels = [s[0] for s in status_distribution]
    status_values = [s[1] for s in status_distribution]

    # 2. Monthly Revenue (Mocked for now since Lead doesn't have created_at)
    # In a real app, we'd query by month: db.query(func.strftime('%Y-%m', Lead.created_at), func.sum(Lead.source_price))...
    monthly_revenue = [1200, 1900, 1500, 2500, 3200, total_revenue] 
    month_labels = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]

    # 3. Recent Transactions (Top 5 leads)
    recent_transactions = db.query(Lead).order_by(Lead.id.desc()).limit(5).all()
    
    return templates.TemplateResponse("admin/finance_vault.html", {
        "request": request,
        "total_revenue": total_revenue,
        "total_liabilities": total_liabilities,
        "net_profit": net_profit,
        "tasks": tasks,
        "status_labels": json.dumps(status_labels),
        "status_values": json.dumps(status_values),
        "monthly_revenue": json.dumps(monthly_revenue),
        "month_labels": json.dumps(month_labels),
        "recent_transactions": recent_transactions
    })

@router.post("/settle-payout")
async def settle_payout(task_id: int = Form(...), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "settled"
    db.commit()
    
    return RedirectResponse(url="/admin/finance-vault", status_code=303)

@router.post("/generate-flutterwave-link/{lead_id}")
async def generate_payment_link(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    from payments import generate_flutterwave_link
    result = generate_flutterwave_link(lead.id, lead.source_price)
    
    return result

# Outreach Template Management
@router.get("/outreach-templates", response_class=HTMLResponse)
async def outreach_templates(request: Request, db: Session = Depends(get_db)):
    all_templates = db.query(Template).all()
    return templates.TemplateResponse("admin/outreach_templates.html", {"request": request, "templates": all_templates})

@router.post("/templates/add")
async def add_template(
    name: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    db: Session = Depends(get_db)
):
    new_template = Template(name=name, subject=subject, body=body)
    db.add(new_template)
    db.commit()
    return RedirectResponse(url="/admin/outreach-templates", status_code=303)

@router.post("/templates/edit/{template_id}")
async def edit_template(
    template_id: int,
    name: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    db: Session = Depends(get_db)
):
    target_template = db.query(Template).filter(Template.id == template_id).first()
    if not target_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    target_template.name = name
    target_template.subject = subject
    target_template.body = body
    db.commit()
    return RedirectResponse(url="/admin/outreach-templates", status_code=303)

@router.post("/templates/delete/{template_id}")
async def delete_template(template_id: int, db: Session = Depends(get_db)):
    target_template = db.query(Template).filter(Template.id == template_id).first()
    if not target_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(target_template)
    db.commit()
    return RedirectResponse(url="/admin/outreach-templates", status_code=303)
