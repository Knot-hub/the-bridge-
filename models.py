from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    role = Column(String)  # 'admin', 'freelancer'
    gender = Column(String)
    whatsapp = Column(String)
    primary_skill = Column(String)
    custom_skill = Column(String)
    bank_details = Column(String)
    certifications_path = Column(String) # Path to uploaded file

class ScrapedFreelancer(Base):
    __tablename__ = "scraped_freelancers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    profile_link = Column(String, unique=True, index=True)
    skills = Column(String)
    source = Column(String) # e.g., 'LinkedIn', 'Indeed'

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    subject = Column(String)
    body = Column(String) # Supports placeholders like {client_name}, {job_title}

class Lead(Base):
    __tablename__ = "leads"


    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    link = Column(String, unique=True, index=True)
    description = Column(String)
    source_price = Column(Float)
    client_contact = Column(String)
    status = Column(String)  # e.g., 'new', 'assigned', 'completed'

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    assigned_freelancer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_scraped_id = Column(Integer, ForeignKey("scraped_freelancers.id"), nullable=True)
    payout_price = Column(Float)
    status = Column(String)

    lead = relationship("Lead")
    freelancer = relationship("User")
    scraped_freelancer = relationship("ScrapedFreelancer")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_email = Column(String)
    subject = Column(String)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_read = Column(Integer, default=0) # 0 for unread, 1 for read
