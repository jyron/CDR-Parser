# CDR Parser API

A FastAPI-based service for parsing and storing Call Detail Records (CDR) in multiple formats.

## Features

- Parse CDR files in three different formats (basic, extended, hex)
- Store normalized usage records in SQLite database
- Query records via REST API
- Automatic format detection based on record ID

## Project Structure

```
hologram_parser/
├── main.py              # FastAPI application and endpoints
├── models.py            # SQLAlchemy database models
├── cdr_parser.py        # CDR parsing logic
├── database.py          # Database configuration
├── frontend/            # Web interface
│   ├── index.html       # Upload UI and records viewer
│   └── app.js           # JavaScript for upload and filtering
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker orchestration
├── requirements.txt     # Python dependencies
└── input_file.txt       # Sample CDR file
```

## Setup

### Option 1: Docker

#### Prerequisites

- Docker
- Docker Compose

#### Running with Docker

1. Build and start the application:

```bash
docker-compose up --build
```

2. Access the application at http://localhost:8000

The web interface provides:

- File upload for CDR files
- Records viewer with filtering and sorting
- Interactive API documentation at `/docs`

3. Stop the application:

```bash
docker-compose down
```

#### Data Persistence

The SQLite database is stored in a Docker volume named `cdr_data`, ensuring data persists across container restarts.

To completely remove the database and start fresh:

```bash
docker-compose down -v
```

### Option 2: Local Python Installation

#### Prerequisites

- Python 3.8 or higher
- pip

#### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the server:

```bash
python3 -m uvicorn main:app --reload
```

The server will run at http://localhost:8000

## Usage

### Web Interface

Open http://localhost:8000 in your browser to access the web interface where you can:

- Upload CDR files for parsing
- View all stored records in a table
- Filter records by any field
- Sort records by bytes used

### API Endpoints

### 1. Upload CDR File

Upload and parse a CDR file.

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@input_file.txt"
```

**Response:**

```json
{
  "message": "File processed successfully",
  "records_processed": 6,
  "records_stored": 6,
  "filename": "input_file.txt"
}
```

### 2. Get All Records

Retrieve all stored usage records.

```bash
curl "http://localhost:8000/records"
```

**Response:**

```json
[
  {
    "id": 4,
    "mnc": 0,
    "bytes_used": 495594,
    "dmcc": "0d39f",
    "cellid": 214,
    "ip": null
  },
  {
    "id": 16,
    "mnc": 48771,
    "bytes_used": 12921,
    "dmcc": null,
    "cellid": 0,
    "ip": "192.99.230.61"
  }
]
```

### 3. Get Record by ID

Retrieve a specific record by its ID.

```bash
curl "http://localhost:8000/records/16"
```

**Response:**

```json
{
  "id": 16,
  "mnc": 48771,
  "bytes_used": 12921,
  "dmcc": null,
  "cellid": 0,
  "ip": "192.99.230.61"
}
```

**404 Response (if not found):**

```json
{
  "detail": "Record with ID 16 not found"
}
```

## CDR Format Specifications

### Format Detection

The parser automatically determines the format based on the last digit of the ID:

- **IDs ending in 4**: Extended format
- **IDs ending in 6**: Hex format
- **All other IDs**: Basic format

### Basic Format

Comma-separated values: `<id>,<bytes_used>`

Example: `9991,2935`

### Extended Format

Comma-separated values: `<id>,<dmcc>,<mnc>,<bytes_used>,<cellid>`

Example: `4,0d39f,0,495594,214`

### Hex Format

Two comma-separated values: `<id>,<hex_string>`

The hex string is 24 characters (12 bytes) with fixed positions:

- Bytes 1-2 (chars 0-3): `mnc`
- Bytes 3-4 (chars 4-7): `bytes_used`
- Bytes 5-8 (chars 8-15): `cellid`
- Bytes 9-12 (chars 16-23): `ip` (each byte is one IP segment)

Example: `16,be833279000000c063e5e63d`

- mnc: `be83` = 48771
- bytes_used: `3279` = 12921
- cellid: `00000000` = 0
- ip: `c0.63.e5.e6.3d` = `192.99.229.230.61`

## API Documentation

FastAPI provides interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database

Records are stored in a SQLite database (`data/cdr_records.db`) with the following schema:

| Field      | Type    | Nullable         |
| ---------- | ------- | ---------------- |
| id         | INTEGER | No (Primary Key) |
| mnc        | INTEGER | Yes              |
| bytes_used | INTEGER | Yes              |
| dmcc       | STRING  | Yes              |
| cellid     | INTEGER | Yes              |
| ip         | STRING  | Yes              |

## Testing

The project includes a sample file `input_file.txt` with example CDR records in all three formats.

You can upload it using the web interface at http://localhost:8000 or via curl:

```bash
curl -X POST "http://localhost:8000/upload" -F "file=@input_file.txt"
```

Query the records:

```bash
curl "http://localhost:8000/records"
```
