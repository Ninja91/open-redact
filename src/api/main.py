from fastapi import FastAPI, Depends, HTTPException
from mcp.server.fastapi import FastMCP
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from src.models.database import Base, User, RemovalRequest, RequestStatus
from src.brokers.example_broker import ExampleBroker
import os

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
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
    return ["ExampleDataBroker"]

@mcp.tool()
async def register_user(full_name: str, email: str, phone: str = None):
    """Register a user for data removal tracking."""
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return f"User with email {email} is already registered."
        
        new_user = User(full_name=full_name, email=email, phone=phone)
        db.add(new_user)
        db.commit()
        return f"User {full_name} registered successfully."
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
        
        # In a real app, we'd lookup the broker class from a registry
        if broker_name != "ExampleDataBroker":
            return f"Broker {broker_name} is not supported yet."
            
        broker = ExampleBroker()
        result = await broker.submit_opt_out(user)
        
        request = RemovalRequest(
            user_id=user.id,
            broker_name=broker_name,
            status=RequestStatus.SUBMITTED if result["status"] == "submitted" else RequestStatus.FAILED,
            external_id=result.get("external_id")
        )
        db.add(request)
        db.commit()
        return f"Removal request submitted to {broker_name}. Tracking ID: {result.get('external_id')}"
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "OpenRedact API is running", "database": "connected" if DATABASE_URL else "missing"}

# Hook the MCP server into FastAPI
app.mount("/mcp", mcp.app)
