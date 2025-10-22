from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import UsageRecord
from cdr_parser import parse_cdr_line

router = APIRouter()


@router.get("/")
def api_info():
    """API information endpoint"""
    return {
        "message": "CDR Parser API",
        "endpoints": {
            "upload": "POST /api/upload",
            "get_all": "GET /api/records",
            "get_by_id": "GET /api/records/{id}"
        }
    }


@router.post("/upload")
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


@router.get("/records")
def get_all_records(db: Session = Depends(get_db)):
    """
    Get all usage records from the database.
    
    Returns:
        List of all usage records in normalized format
    """
    records = db.query(UsageRecord).all()
    return [record.to_dict() for record in records]


@router.get("/records/{record_id}")
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

