# DocSense

DocSense is a local backend for uploading, storing, downloading, analyzing, and organizing text documents.

The project is built around a simple idea: a user uploads documents, the backend stores files and metadata, and an external ML component can download documents that still need analysis, detect their topic, and send the result back to the backend.

This repository contains the backend part of the project. The ML implementation can be developed separately and connected through the documented API contract.

## Current State

The preparation stage is mostly complete. The backend can already work with documents as files and as database records.

Implemented:

- single document upload;
- bulk document upload;
- saving files into the local `uploads/` directory;
- saving document metadata in SQLite;
- duplicate filename protection;
- listing documents;
- filtering documents by status;
- getting one document by id;
- downloading one document by id;
- downloading a ZIP archive of documents for analysis;
- single document deletion;
- bulk document deletion;
- updating analysis result for one document;
- bulk update of document analysis results;
- `uploaded`, `processed`, and `failed` document statuses;
- maintenance endpoint for checking and cleaning inconsistent file/database state;
- Swagger UI documentation through FastAPI.

## Document Flow

Basic flow:

```text
upload document(s)
-> backend saves files to uploads/
-> backend creates Document records in SQLite
-> external ML service downloads documents for analysis
-> ML service detects topic or marks document as failed
-> ML service sends analysis result back to backend
-> backend updates status and topic
```

Current document statuses:

```text
uploaded  - document was uploaded and waits for analysis
processed - document was successfully analyzed and has a topic
failed    - analysis failed, topic may be empty
```

## ML Integration

The ML service is expected to be external to the backend. It can be a local script, a separate service, or a private module.

The backend exposes two main endpoints for ML integration.

### Download Documents For Analysis

```http
GET /api/v1/documents/download
```

Returns a ZIP archive with documents that should be analyzed.

Files inside the archive are named with the document id prefix:

```text
12__invoice.txt
15__contract.txt
```

The id prefix allows the ML service to understand which database record should be updated after analysis.

### Send Analysis Results

```http
PATCH /api/v1/documents/analysis
```

Example request body:

```json
[
  {
    "document_ids": [12, 15],
    "status": "processed",
    "topic": "financial documents"
  },
  {
    "document_ids": [18],
    "status": "failed",
    "topic": null
  }
]
```

Rules:

- `processed` means the document was analyzed successfully;
- `processed` requires a topic;
- `failed` means the document could not be analyzed;
- `failed` may have `topic: null`.

The actual ML code is not required to be part of this repository. The backend only needs the API contract above.

## Technologies

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

## Installation

Clone the repository and open the project folder:

```bash
git clone https://github.com/skyland228/docsense.git
cd docsense
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run

```powershell
python -m docsense.main
```

After startup:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

## API Overview

### Upload One Document

```http
POST /api/v1/documents/upload
```

The request uses `multipart/form-data`. The file is sent in the `file` field.

### Upload Multiple Documents

```http
POST /api/v1/documents/upload/bulk
```

The request uses `multipart/form-data`. Files are sent in the `files` field.

### Get Documents

```http
GET /api/v1/documents
```

With status filter:

```http
GET /api/v1/documents?status=uploaded
GET /api/v1/documents?status=processed
GET /api/v1/documents?status=failed
```

### Get One Document

```http
GET /api/v1/documents/{document_id}
```

Returns document metadata as JSON.

### Download One Document

```http
GET /api/v1/documents/{document_id}/download
```

Returns the stored file.

### Download Documents For Analysis

```http
GET /api/v1/documents/download
```

Returns a ZIP archive for the external ML service.

### Update One Analysis Result

```http
PATCH /api/v1/documents/{document_id}/analysis
```

Example:

```json
{
  "status": "processed",
  "topic": "financial documents"
}
```

### Bulk Update Analysis Results

```http
PATCH /api/v1/documents/analysis
```

Example:

```json
[
  {
    "document_ids": [1, 2, 3],
    "status": "processed",
    "topic": "legal documents"
  }
]
```

### Delete One Document

```http
DELETE /api/v1/documents/{document_id}
```

Deletes the file from `uploads/` and removes the database record.

### Delete Multiple Documents

```http
DELETE /api/v1/documents
```

Example:

```json
{
  "ids": [1, 2, 3]
}
```

## Project Structure

```text
docsense/
|-- api/            # FastAPI routers
|-- data_base/      # database setup and SQLAlchemy models
|-- repositories/   # database queries
|-- services/       # business logic and file operations
|-- dependencies.py # FastAPI dependencies
|-- schemas.py      # Pydantic schemas
`-- main.py         # application creation and startup
```

## Current Plan

The next step is document organization after analysis.

Planned near-term feature:

```text
if a document has a topic
-> create a folder for this topic if it does not exist
-> move/copy the document into that topic folder
```

Possible future development:

- full document analysis, not only topic detection;
- extracting key facts from documents;
- search by topic and content;
- retrying failed analysis;
- local UI for working with documents;
- better maintenance tools for file/database consistency;
- optional integration with a private ML service.

## Repository Note

This repository is focused on the backend. Runtime files, uploaded documents, temporary ML folders, and private ML scripts should not be committed.
