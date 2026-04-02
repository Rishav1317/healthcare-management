"""
FastAPI Backend for Healthcare Recovery Forecast
Serves API endpoints including PDF report generation
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from pathlib import Path
import tempfile
from datetime import datetime, timedelta
import json

# Add ml module to path
ml_path = os.path.join(os.path.dirname(__file__), 'ml')
sys.path.insert(0, ml_path)

from ml.pdf_report_generator import generate_pdf_report

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Recovery Forecast API",
    description="API for healthcare recovery predictions and reporting",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:9000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Authentication Endpoints ====================

@app.post("/api/auth/login")
async def login(data: dict):
    """Mock authentication endpoint"""
    hospital_id = data.get("hospitalId")
    password = data.get("password")
    
    if hospital_id and password:
        return {
            "success": True,
            "token": f"mock_token_{hospital_id}",
            "user": {
                "id": "1",
                "hospitalId": hospital_id,
                "name": "Dr. Sarah Johnson",
                "email": "sarah@hospital.com",
                "role": "admin"
            }
        }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/api/auth/logout")
async def logout():
    """Logout endpoint"""
    return {"success": True, "message": "Logged out successfully"}


# ==================== Upload Endpoints ====================

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), hospital_id: str = ""):
    """Handle file uploads"""
    try:
        contents = await file.read()
        return {
            "success": True,
            "filename": file.filename,
            "size": len(contents),
            "hospital_id": hospital_id,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Prediction Endpoints ====================

@app.post("/api/predict/batch")
async def batch_predict(data: dict):
    """Batch prediction endpoint"""
    try:
        patients = data.get("patients", [])
        
        # Mock predictions
        predictions = []
        for patient in patients:
            predictions.append({
                "patientId": patient.get("id"),
                "predictedLOS": 7,
                "confidence": 0.92,
                "severity": patient.get("severity", 3),
                "factors": ["Age", "Comorbidity", "Vital Signs"]
            })
        
        return {
            "success": True,
            "predictions": predictions,
            "totalProcessed": len(patients)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/predict/single")
async def single_predict(patient_data: dict):
    """Single patient prediction"""
    return {
        "success": True,
        "prediction": {
            "patientId": patient_data.get("id"),
            "predictedLOS": 7,
            "confidence": 0.92,
            "severity": patient_data.get("severity", 3),
            "factors": ["Age", "Comorbidity", "Vital Signs"]
        }
    }


@app.get("/api/predict/explain/{patient_id}")
async def explain_prediction(patient_id: str):
    """Get prediction explanation for a patient"""
    return {
        "success": True,
        "patientId": patient_id,
        "explanation": {
            "features": ["Age", "Severity Level", "Comorbidities", "Vital Signs", "Lab Results"],
            "importance": [0.28, 0.24, 0.18, 0.15, 0.12]
        }
    }


# ==================== Dashboard Endpoints ====================

@app.get("/api/dashboard")
async def get_dashboard_data():
    """Get dashboard statistics and data"""
    return {
        "success": True,
        "statistics": {
            "totalPatients": 464,
            "averageLOS": 6.2,
            "criticalCases": 24,
            "bedUtilization": 0.78
        },
        "bedOccupancy": {
            "days": list(range(1, 15)),
            "occupancy": [75, 78, 80, 77, 79, 81, 78, 76, 80, 82, 79, 77, 81, 78]
        },
        "severityDistribution": {
            "level1": 45,
            "level2": 120,
            "level3": 180,
            "level4": 95,
            "level5": 24
        }
    }


# ==================== Report Endpoints ====================

@app.get("/api/reports/pdf")
async def generate_report(hospital_name: str = "Central Medical Center"):
    """Generate and download comprehensive PDF report"""
    try:
        # Create temporary directory for PDF
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(temp_dir, f"Recovery_Forecast_Report_{timestamp}.pdf")
        
        # Generate PDF
        generate_pdf_report(hospital_name=hospital_name, output_path=output_path)
        
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"PDF generation failed")
        
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=f"Recovery_Forecast_Report_{timestamp}.pdf"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")


@app.post("/api/reports/patient")
async def generate_patient_report(patient_data: dict):
    """Generate patient-specific report (mock)"""
    return {
        "success": True,
        "reportId": "RPT001",
        "patientName": patient_data.get("name"),
        "generatedAt": datetime.now().isoformat(),
        "message": "Patient report generated successfully"
    }


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Healthcare Recovery Forecast API",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Healthcare Recovery Forecast API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "auth": {
                "login": "POST /api/auth/login",
                "logout": "POST /api/auth/logout"
            },
            "predictions": {
                "batch": "POST /api/predict/batch",
                "single": "POST /api/predict/single",
                "explain": "GET /api/predict/explain/{patient_id}"
            },
            "dashboard": "GET /api/dashboard",
            "reports": {
                "pdf": "GET /api/reports/pdf?hospital_name=Hospital%20Name",
                "patient": "POST /api/reports/patient"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
