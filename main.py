from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import UsageRecord
from cdr_parser import parse_cdr_line

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CDR Parser API",
    description="API for parsing and storing Call Detail Records",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api")
def api_info():
    """API information endpoint"""
    return {
        "message": "CDR Parser API",
        "endpoints": {
            "upload": "POST /upload",
            "get_all": "GET /records",
            "get_by_id": "GET /records/{id}"
        }
    }


@app.post("/upload")
async def upload_cdr_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse a CDR file.
    
    Accepts a text file with CDR records (one per line).
    Parses each record according to its format and stores in database.
    
    Returns:
        Count of records processed and stored
    """
    content = await file.read()
    lines = content.decode('utf-8').split('\n')
    
    records_processed = 0
    records_stored = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        records_processed += 1
        
        try:
            parsed_data = parse_cdr_line(line)
            if parsed_data:
                # Check if record with this ID already exists
                existing = db.query(UsageRecord).filter(
                    UsageRecord.id == parsed_data["id"]
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in parsed_data.items():
                        setattr(existing, key, value)
                else:
                    # Create new record
                    record = UsageRecord(**parsed_data)
                    db.add(record)
                
                records_stored += 1
        except Exception as e:
            print(f"Error parsing line '{line}': {e}")
            continue
    
    db.commit()
    
    return {
        "message": "File processed successfully",
        "records_processed": records_processed,
        "records_stored": records_stored,
        "filename": file.filename
    }


@app.get("/records")
def get_all_records(db: Session = Depends(get_db)):
    """
    Get all usage records from the database.
    
    Returns:
        List of all usage records in normalized format
    """
    records = db.query(UsageRecord).all()
    return [record.to_dict() for record in records]


@app.get("/records/{record_id}")
def get_record_by_id(record_id: int, db: Session = Depends(get_db)):
    """
    Get a single usage record by ID.
    
    Args:
        record_id: The ID of the record to retrieve
        
    Returns:
        Usage record in normalized format
        
    Raises:
        404: If record with given ID is not found
    """
    record = db.query(UsageRecord).filter(UsageRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail=f"Record with ID {record_id} not found")
    
    return record.to_dict()


# Mount frontend static files (must be last to not override API routes)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

