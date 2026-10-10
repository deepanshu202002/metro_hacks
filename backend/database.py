import os
import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

BACKEND_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BACKEND_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'metro.db')

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODEL DEFINITIONS ---

class TimetableVersion(Base):
    __tablename__ = "timetable_versions"

    id = Column(Integer, primary_key=True, index=True)
    version_tag = Column(String(50), unique=True, index=True) # e.g. "v1.0.0"
    status = Column(String(30), default="draft") # draft | pending_approval | published | archived
    effective_from = Column(String(50))
    created_by = Column(String(100))
    approved_by = Column(String(100), nullable=True)
    note = Column(Text, default="")
    created_at = Column(String(50))
    published_at = Column(String(50), nullable=True)

    trips = relationship("TripRecord", back_populates="version", cascade="all, delete-orphan")
    headways = relationship("HeadwayRuleRecord", back_populates="version", cascade="all, delete-orphan")

class TripRecord(Base):
    __tablename__ = "trip_records"

    id = Column(String(100), primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("timetable_versions.id"), primary_key=True)
    line = Column(String(50))
    service = Column(String(100))
    direction = Column(String(30))
    stop_times_json = Column(Text) # JSON list: [{station_id, arrival, departure}]

    version = relationship("TimetableVersion", back_populates="trips")

class HeadwayRuleRecord(Base):
    __tablename__ = "headway_rule_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version_id = Column(Integer, ForeignKey("timetable_versions.id"))
    line = Column(String(50))
    first_train = Column(String(20))
    last_train = Column(String(20))
    headway_peak_min = Column(Integer)
    headway_offpeak_min = Column(Integer)
    speed_kmh = Column(Integer, default=35)
    dwell_sec = Column(Integer, default=25)

    version = relationship("TimetableVersion", back_populates="headways")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user = Column(String(100))
    role = Column(String(50))
    action = Column(String(100)) # e.g. "PROPOSE_TIMING_CHANGE", "APPROVE_VERSION", "PUBLISH_VERSION", "ROLLBACK"
    target = Column(String(100)) # e.g. "Trip VIOLET_SHUTTLE_UP_1", "Version v1.1.0"
    before_val = Column(Text, nullable=True)
    after_val = Column(Text, nullable=True)
    ip_address = Column(String(50), default="127.0.0.1")
    timestamp = Column(String(50))

class ComplaintRecord(Base):
    __tablename__ = "complaints"

    ticket_id = Column(String(50), primary_key=True, index=True)
    category = Column(String(50)) # cleanliness, crowding, delay, broken_lift_escalator, safety, staff_behaviour, ticketing, lost_found, accessibility, other
    station_id = Column(String(50))
    line = Column(String(50), nullable=True)
    description = Column(Text)
    photo_url = Column(String(255), nullable=True)
    contact = Column(String(100), nullable=True)
    status = Column(String(30), default="received") # received | assigned | in_progress | resolved
    priority = Column(String(30), default="medium") # low | medium | high | urgent
    sentiment = Column(String(30), default="neutral") # negative | neutral | positive
    assigned_to = Column(String(100), nullable=True)
    internal_notes = Column(Text, default="")
    ai_triage_json = Column(Text, nullable=True)
    ai_draft_reply = Column(Text, nullable=True)
    created_at = Column(String(50))
    updated_at = Column(String(50))

class StaffIncident(Base):
    __tablename__ = "staff_incidents"

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(200))
    station_id = Column(String(50), nullable=True)
    line = Column(String(50), nullable=True)
    priority = Column(String(30), default="routine") # routine | high | urgent
    category = Column(String(50), default="shift_handover") # shift_handover | track_fault | passenger_crowd | sop_incident
    content = Column(Text)
    author = Column(String(100))
    role = Column(String(50))
    acknowledgements_json = Column(Text, default="[]") # list of usernames who acknowledged
    linked_ticket_id = Column(String(50), nullable=True)
    created_at = Column(String(50))

class AssetRecord(Base):
    __tablename__ = "assets"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100))
    station_id = Column(String(50))
    type = Column(String(50)) # escalator | lift | door | hvac | track_circuit
    health_score = Column(Integer, default=95) # 0 to 100
    predicted_failure_window = Column(String(100), default="Normal")
    status = Column(String(50), default="operational") # operational | attention_required | maintenance_in_progress
    work_order_id = Column(String(50), nullable=True)
    technician_notes = Column(Text, default="")
    cost_avoided_inr = Column(Integer, default=0)
    last_inspected = Column(String(50))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully in SQLite.")
