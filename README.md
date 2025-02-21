# Stable Mail Processor

This application processes mail items from the Stable API, uploads their scanned PDFs to Google Drive, and keeps track of processed items in a SQLite database.

## Features

- Fetches mail items from Stable API
- Organizes PDFs in Google Drive folders by recipient
- Tracks processed mail items to avoid duplicates
- Uses service-based architecture for maintainability
- Docker support for easy deployment

## Prerequisites

- Python 3.12+
- Google Cloud Service Account with Drive API access
- Stable API key
- Docker (optional)

## Setup

1. Clone the repository:
   ``` bash
    git clone <repository-url>
    cd stable-mail-processor
   ```
2. Create a virtual environment (optional but recommended):
   ``` bash
    python -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ``` bash
    pip install -r requirements.txt
   ```
4. Configure environment variables:
   
    Create a `.env` file with:
    ``` bash
    STABLE_API_KEY=your_stable_api_key
    ```
5. Set up Google Drive API:
   - Place your Google Cloud service account key in `secrets.json`
   - Ensure the service account has access to Google Drive.

## Running the Application

### Using Python directly:
``` bash
make run
```

### Using Docker:
``` bash
docker-compose up --build
```

## Project Structure
```
├── src/
│ ├── services/
│ │ ├── init.py
│ │ ├── google_drive.py
│ │ ├── sqlite_db.py
│ │ └── stable_mail.py
│ ├── config.py
│ └── main.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```