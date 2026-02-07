from fastapi import FastAPI, Depends, HTTPException
from mcp.server.fastmcp import FastMCP
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from src.models.database import Base, User, RemovalRequest, RequestStatus
from src.brokers.example_broker import ExampleBroker
from src.brokers.cyber_background_checks import CyberBackgroundChecks
from src.brokers.official_usa import OfficialUSA
from src.brokers.true_people_search import TruePeopleSearch
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="OpenRedact MCP Server")
mcp = FastMCP("OpenRedact")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@mcp.tool()
async def list_supported_brokers():
    """Returns a list of data brokers currently supported for removal."""
    return ["ExampleDataBroker", "CyberBackgroundChecks", "OfficialUSA", "TruePeopleSearch"]

@mcp.tool()
async def register_user(full_name: str, email: str, phone: str = None, city: str = None, state: str = None):
    """Register a user for data removal tracking. State should be 2-letter code (e.g., NY)."""
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return f"User with email {email} is already registered."
        
        new_user = User(full_name=full_name, email=email, phone=phone, city=city, state=state)
        db.add(new_user)
        db.commit()
        return f"User {full_name} registered successfully."
    finally:
        db.close()

@mcp.tool()
async def get_scraped_data(user_email: str):
    """View all personal information discovered about you across different data brokers."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            return "User not found."
        
        requests = db.query(RemovalRequest).filter(RemovalRequest.user_id == user.id).all()
        findings = {}
        for r in requests:
            if r.scraped_data:
                findings[r.broker_name] = r.scraped_data
        
        return findings if findings else "No data has been scraped yet. Run 'start_removal' first."
    finally:
        db.close()

@mcp.tool()
async def start_removal(user_email: str, broker_name: str):
    """Initiate a removal request for a specific user and broker."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            return "User not found. Please register first."
        
        brokers = {
            "ExampleDataBroker": ExampleBroker(),
            "CyberBackgroundChecks": CyberBackgroundChecks(),
            "OfficialUSA": OfficialUSA(),
            "TruePeopleSearch": TruePeopleSearch()
        }
        
        broker = brokers.get(broker_name)
        if not broker:
            return f"Broker {broker_name} is not supported yet."
            
        result = await broker.submit_opt_out(user)
        
        status_map = {
            "submitted": RequestStatus.SUBMITTED,
            "pending": RequestStatus.PENDING,
            "completed": RequestStatus.COMPLETED,
            "failed": RequestStatus.FAILED
        }
        
        request = RemovalRequest(
            user_id=user.id,
            broker_name=broker_name,
            status=status_map.get(result.get("status"), RequestStatus.FAILED),
            external_id=result.get("external_id"),
            scraped_data=result.get("scraped_data", {}),
            logs=[result.get("message") or result.get("error")]
        )
        db.add(request)
        db.commit()
        
        found_data = f" Discovered: {result.get('scraped_data')}" if result.get('scraped_data') else ""
        return f"Status: {result.get('status')}. Message: {result.get('message') or result.get('error')}.{found_data}"
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "OpenRedact API is running", "database": "connected" if DATABASE_URL else "missing"}

# Hook the MCP server into FastAPI
app.mount("/mcp", mcp.sse_app())
