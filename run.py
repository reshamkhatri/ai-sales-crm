"""
AI Sales Assistant - Main Entry Point
Run this to start the dashboard and initialize the database.
"""

from database import db
from dashboard import app

def main():
    print("=== AI Sales Assistant ===")
    print("Starting dashboard at http://localhost:8000")
    import uvicorn
    uvicorn.run("dashboard.app:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
