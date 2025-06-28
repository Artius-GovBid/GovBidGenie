from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Opportunity(Base):
    __tablename__ = 'opportunities'
    id = Column(Integer, primary_key=True)
    sam_gov_id = Column(String(255), nullable=False, unique=True)
    title = Column(Text, nullable=False)
    url = Column(String(2048))
    agency = Column(String(255))
    posted_date = Column(DateTime)
    naics_code = Column(String(50), nullable=True)
    psc_code = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    leads = relationship("Lead", back_populates="opportunity")

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    source = Column(String) 
    status = Column(String(50), default='Discovered')
    azure_devops_work_item_id = Column(Integer, nullable=True)
    business_name = Column(String, nullable=True)
    facebook_page_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'))
    opportunity = relationship("Opportunity", back_populates="leads")
