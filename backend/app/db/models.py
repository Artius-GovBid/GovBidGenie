from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Opportunity(Base):
    __tablename__ = 'opportunities'
    id = Column(Integer, primary_key=True)
    sam_gov_id = Column(String(255), nullable=False, unique=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    agency = Column(String(255))
    location_text = Column(String(255))
    url = Column(String(2048))
    created_at = Column(DateTime, default=datetime.utcnow)
    posted_date = Column(DateTime)

    leads = relationship("Lead", back_populates="opportunity")

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    business_name = Column(String)
    facebook_page_url = Column(String)
    status = Column(String, default='Identified')
    azure_devops_work_item_id = Column(Integer, nullable=True) # To link to Azure DevOps
    analyzed_for_learning = Column(Boolean, default=False) # For Epic 5
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'))
    opportunity = relationship("Opportunity", back_populates="leads")
    
    conversations = relationship("ConversationLog", back_populates="lead")

class ConversationLog(Base):
    __tablename__ = 'conversation_logs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sender = Column(String) # 'AI' or 'Business'
    message = Column(Text)

    lead_id = Column(Integer, ForeignKey('leads.id'))
    lead = relationship("Lead", back_populates="conversations")

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    title = Column(String)
    status = Column(String, default='tentative') # tentative, confirmed, cancelled
    external_event_id = Column(String) # To store the ID from Outlook/Google Calendar
    created_at = Column(DateTime, default=datetime.utcnow)
    
    lead_id = Column(Integer, ForeignKey('leads.id'))
    lead = relationship("Lead")

# The PRD also mentioned a learnings table for Epic 5. I'll add it now.
class Learning(Base):
    __tablename__ = 'learnings'
    id = Column(Integer, primary_key=True)
    outcome_tag = Column(String)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation_id = Column(Integer, ForeignKey('conversation_logs.id'))
    conversation = relationship("ConversationLog")
