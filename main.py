from fastapi import FastAPI, Request, Header, Depends
from fastapi.staticfiles import StaticFiles
from database import engine, Base, get_db
from routers import storefront, admin, portal
from models import Lead
from sqlalchemy.orm import Session
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="The Bridge")

# Secret hash for webhook verification (In production, use ENV VARIABLE)
FLUTTERWAVE_SECRET_HASH = "the_bridge_secret_123"

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Webhook for Flutterwave
@app.post("/webhook/flutterwave")
async def flutterwave_webhook(
    request: Request, 
    verif_hash: str = Header(None, alias="verif-hash"),
    db: Session = Depends(get_db)
):
    # Security Check: Ensure the signal is real
    if not verif_hash or verif_hash != FLUTTERWAVE_SECRET_HASH:
        return {"status": "error", "message": "Invalid signature"}

    payload = await request.json()
    
    # Process successful payment
    if payload.get("status") == "successful":
        tx_ref = payload.get("txRef") # e.g., "BL-L1-abcd"
        if tx_ref and tx_ref.startswith("BL-L"):
            try:
                lead_id = int(tx_ref.split("-")[1][1:])
                lead = db.query(Lead).filter(Lead.id == lead_id).first()
                if lead:
                    lead.status = "PAID"
                    db.commit()
            except Exception as e:
                print(f"Webhook processing error: {e}")

    return {"status": "success"}

# Register routers
app.include_router(storefront.router)
app.include_router(admin.router)
app.include_router(portal.router)
