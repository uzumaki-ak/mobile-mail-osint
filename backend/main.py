from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import asyncio
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
import uuid

from services.phone_intel_advanced import AdvancedPhoneIntelService
from models.phone_data import PhoneIntelResponse, ScanRequest, ScanStatus

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/errors.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI(title="Advanced Phone Intelligence Toolkit", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output directories
os.makedirs("output/raw", exist_ok=True)
os.makedirs("output/images", exist_ok=True)
os.makedirs("output", exist_ok=True)

# In-memory storage for scan status
scan_status: Dict[str, Dict] = {}
phone_intel_service = AdvancedPhoneIntelService()

@app.post("/api/scan", response_model=Dict[str, str])
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """Start comprehensive phone number intelligence scan"""
    scan_id = str(uuid.uuid4())
    
    # Initialize scan status
    scan_status[scan_id] = {
        "phone_number": request.phone_number,
        "status": "started",
        "progress": 0,
        "features": {
            "basic_info": "pending",
            "geolocation": "pending", 
            "owner_spam": "pending",
            "messaging": "pending",
            "social_media": "pending",
            "breach_data": "pending",
            "spam_reports": "pending",
            "domain_whois": "pending",
            "profile_images": "pending",
            "reassignment": "pending",
            "online_mentions": "pending"
        },
        "started_at": datetime.now().isoformat(),
        "errors": []
    }
    
    # Start background scan
    background_tasks.add_task(run_comprehensive_scan, scan_id, request.phone_number)
    
    return {"scan_id": scan_id, "status": "started"}

@app.get("/api/scan/{scan_id}/status")
async def get_scan_status(scan_id: str):
    """Get scan status and progress"""
    if scan_id not in scan_status:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return scan_status[scan_id]

@app.get("/api/scan/{scan_id}/results")
async def get_scan_results(scan_id: str):
    """Get final scan results"""
    if scan_id not in scan_status:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    status = scan_status[scan_id]
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Scan not completed yet")
    
    phone_number = status["phone_number"]
    results_file = f"output/{phone_number.replace('+', '').replace(' ', '')}.json"
    
    if not os.path.exists(results_file):
        raise HTTPException(status_code=404, detail="Results file not found")
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    return results

@app.get("/api/download/{phone_number}/{file_type}")
async def download_file(phone_number: str, file_type: str):
    """Download results in different formats"""
    clean_number = phone_number.replace('+', '').replace(' ', '')
    file_map = {
        "json": f"output/{clean_number}.json",
        "csv": f"output/{clean_number}.csv", 
        "pdf": f"output/{clean_number}.pdf"
    }
    
    if file_type not in file_map:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_path = file_map[file_type]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        filename=f"{clean_number}.{file_type}",
        media_type="application/octet-stream"
    )

async def run_comprehensive_scan(scan_id: str, phone_number: str):
    """Run complete phone intelligence scan with all features"""
    try:
        # Update status
        scan_status[scan_id]["status"] = "running"
        
        # Run all features with comprehensive scraping
        results = await phone_intel_service.comprehensive_scan(
            phone_number, 
            lambda feature, status: update_feature_status(scan_id, feature, status)
        )
        
        # Save final results
        clean_number = phone_number.replace('+', '').replace(' ', '')
        output_file = f"output/{clean_number}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Generate CSV and PDF
        await phone_intel_service.export_comprehensive_results(clean_number, results)
        
        # Update final status
        scan_status[scan_id]["status"] = "completed"
        scan_status[scan_id]["progress"] = 100
        scan_status[scan_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        logging.error(f"Comprehensive scan failed for {phone_number}: {str(e)}")
        scan_status[scan_id]["status"] = "failed"
        scan_status[scan_id]["error"] = str(e)
        scan_status[scan_id]["errors"].append({
            "feature": "general",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

def update_feature_status(scan_id: str, feature: str, status: str):
    """Update individual feature status"""
    if scan_id in scan_status:
        scan_status[scan_id]["features"][feature] = status
        
        # Calculate progress
        completed = sum(1 for s in scan_status[scan_id]["features"].values() 
                       if s in ["success", "failed"])
        total = len(scan_status[scan_id]["features"])
        scan_status[scan_id]["progress"] = int((completed / total) * 100)

@app.get("/")
async def root():
    return {"message": "Advanced Phone Intelligence Toolkit API v2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
