import json
import os
import asyncio
from pathlib import Path
from quart import Quart, send_file, jsonify, request
from quart_cors import cors
import pydicom
import aiofiles
from typing import Dict, List, Any

app = Quart(__name__)
app = cors(app, allow_origin="*")

# Directory where DICOM files are stored
DICOM_DIR = Path("/app/dicom_files")

class DicomService:
    def __init__(self, dicom_dir: Path):
        self.dicom_dir = dicom_dir
        self._studies_cache = None
    
    async def _load_dicom_file(self, file_path: Path) -> Dict[str, Any]:
        """Load DICOM file and extract metadata"""
        try:
            ds = pydicom.dcmread(file_path)
            
            # Extract basic metadata
            metadata = {
                "SOPInstanceUID": getattr(ds, 'SOPInstanceUID', ''),
                "StudyInstanceUID": getattr(ds, 'StudyInstanceUID', ''),
                "SeriesInstanceUID": getattr(ds, 'SeriesInstanceUID', ''),
                "PatientName": str(getattr(ds, 'PatientName', '')),
                "PatientID": getattr(ds, 'PatientID', ''),
                "StudyDescription": getattr(ds, 'StudyDescription', ''),
                "SeriesDescription": getattr(ds, 'SeriesDescription', ''),
                "StudyDate": getattr(ds, 'StudyDate', ''),
                "StudyTime": getattr(ds, 'StudyTime', ''),
                "Modality": getattr(ds, 'Modality', ''),
                "InstanceNumber": getattr(ds, 'InstanceNumber', 1),
                "SeriesNumber": getattr(ds, 'SeriesNumber', 1),
            }
            
            # Add image-related metadata if available
            if hasattr(ds, 'Rows'):
                metadata["Rows"] = ds.Rows
            if hasattr(ds, 'Columns'):
                metadata["Columns"] = ds.Columns
            if hasattr(ds, 'PixelSpacing'):
                metadata["PixelSpacing"] = list(ds.PixelSpacing)
            if hasattr(ds, 'ImageOrientationPatient'):
                metadata["ImageOrientationPatient"] = list(ds.ImageOrientationPatient)
            if hasattr(ds, 'ImagePositionPatient'):
                metadata["ImagePositionPatient"] = list(ds.ImagePositionPatient)
            if hasattr(ds, 'SliceThickness'):
                metadata["SliceThickness"] = str(ds.SliceThickness)
            
            return metadata
        except Exception as e:
            print(f"Error loading DICOM file {file_path}: {e}")
            return {}
    
    async def _scan_dicom_files(self) -> Dict[str, Any]:
        """Scan DICOM directory and build study structure"""
        if self._studies_cache:
            return self._studies_cache
        
        studies = {}
        
        if not self.dicom_dir.exists():
            return {"studies": []}
        
        # Walk through all DICOM files
        for file_path in self.dicom_dir.rglob("*.dcm"):
            metadata = await self._load_dicom_file(file_path)
            if not metadata:
                continue
            
            study_uid = metadata["StudyInstanceUID"]
            series_uid = metadata["SeriesInstanceUID"]
            
            # Initialize study if not exists
            if study_uid not in studies:
                studies[study_uid] = {
                    "StudyInstanceUID": study_uid,
                    "StudyDescription": metadata["StudyDescription"],
                    "StudyDate": metadata["StudyDate"],
                    "StudyTime": metadata["StudyTime"],
                    "PatientName": metadata["PatientName"],
                    "PatientId": metadata["PatientID"],
                    "series": []
                }
            
            study = studies[study_uid]
            
            # Find or create series
            series = None
            for s in study["series"]:
                if s["SeriesInstanceUID"] == series_uid:
                    series = s
                    break
            
            if not series:
                series = {
                    "SeriesInstanceUID": series_uid,
                    "SeriesDescription": metadata["SeriesDescription"],
                    "SeriesNumber": metadata["SeriesNumber"],
                    "SeriesDate": metadata["StudyDate"],
                    "SeriesTime": metadata["StudyTime"],
                    "Modality": metadata["Modality"],
                    "instances": []
                }
                study["series"].append(series)
            
            # Add instance
            instance = {
                "metadata": metadata,
                "url": f"dicomweb://localhost:5000/dicom/file/{file_path.name}"
            }
            series["instances"].append(instance)
        
        # Sort instances within each series
        for study in studies.values():
            for series in study["series"]:
                series["instances"].sort(key=lambda x: x["metadata"].get("InstanceNumber", 0))
        
        result = {"studies": list(studies.values())}
        self._studies_cache = result
        return result

# Initialize DICOM service
dicom_service = DicomService(DICOM_DIR)

@app.route('/api/studies', methods=['GET'])
async def get_studies():
    """Get all studies"""
    try:
        studies_data = await dicom_service._scan_dicom_files()
        return jsonify(studies_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/studies/<study_uid>', methods=['GET'])
async def get_study(study_uid: str):
    """Get specific study"""
    try:
        studies_data = await dicom_service._scan_dicom_files()
        for study in studies_data["studies"]:
            if study["StudyInstanceUID"] == study_uid:
                return jsonify(study)
        return jsonify({"error": "Study not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/series/<series_uid>', methods=['GET'])
async def get_series(series_uid: str):
    """Get specific series"""
    try:
        studies_data = await dicom_service._scan_dicom_files()
        for study in studies_data["studies"]:
            for series in study["series"]:
                if series["SeriesInstanceUID"] == series_uid:
                    return jsonify(series)
        return jsonify({"error": "Series not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dicom/file/<filename>', methods=['GET'])
async def get_dicom_file(filename: str):
    """Serve DICOM file"""
    try:
        file_path = None
        for path in DICOM_DIR.rglob("*.dcm"):
            if path.name == filename:
                file_path = path
                break
        
        if not file_path:
            return jsonify({"error": "File not found"}), 404
        
        return await send_file(str(file_path))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dicomweb/studies', methods=['GET'])
async def dicomweb_studies():
    """DICOMweb compatible studies endpoint"""
    try:
        studies_data = await dicom_service._scan_dicom_files()
        # Transform to DICOMweb format
        dicomweb_studies = []
        for study in studies_data["studies"]:
            dicomweb_study = {
                "00120010": {"vr": "UI", "Value": [study["StudyInstanceUID"]]},
                "00120020": {"vr": "DA", "Value": [study["StudyDate"]]},
                "00120030": {"vr": "TM", "Value": [study["StudyTime"]]},
                "00120050": {"vr": "SH", "Value": [study["AccessionNumber"]] if "AccessionNumber" in study else []},
                "00120060": {"vr": "CS", "Value": [study["Modality"]] if "Modality" in study else []},
                "00100010": {"vr": "PN", "Value": [study["PatientName"]]},
                "00100020": {"vr": "LO", "Value": [study["PatientId"]]},
                "00100030": {"vr": "DA", "Value": [study["PatientBirthDate"]] if "PatientBirthDate" in study else []},
                "00100040": {"vr": "CS", "Value": [study["PatientSex"]] if "PatientSex" in study else []}
            }
            dicomweb_studies.append(dicomweb_study)
        
        return jsonify(dicomweb_studies)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dicomweb/studies/<study_uid>', methods=['GET'])
async def dicomweb_study(study_uid: str):
    """DICOMweb compatible study endpoint"""
    try:
        studies_data = await dicom_service._scan_dicom_files()
        for study in studies_data["studies"]:
            if study["StudyInstanceUID"] == study_uid:
                # Transform to DICOMweb format
                dicomweb_series = []
                for series in study["series"]:
                    dicomweb_series_item = {
                        "0020000D": {"vr": "UI", "Value": [study["StudyInstanceUID"]]},
                        "0020000E": {"vr": "UI", "Value": [series["SeriesInstanceUID"]]},
                        "00200011": {"vr": "IS", "Value": [series["SeriesNumber"]]},
                        "00080060": {"vr": "CS", "Value": [series["Modality"]]},
                        "00080021": {"vr": "DA", "Value": [series["SeriesDate"]]},
                        "00080031": {"vr": "TM", "Value": [series["SeriesTime"]]},
                        "0008103E": {"vr": "LO", "Value": [series["SeriesDescription"]]}
                    }
                    dicomweb_series.append(dicomweb_series_item)
                
                return jsonify(dicomweb_series)
        
        return jsonify({"error": "Study not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dicomweb/studies/<study_uid>/series/<series_uid>/instances', methods=['GET'])
async def dicomweb_instances(study_uid: str, series_uid: str):
    """DICOMweb compatible instances endpoint"""
    try:
        studies_data = await dicom_service._scan_dicom_files()
        for study in studies_data["studies"]:
            if study["StudyInstanceUID"] == study_uid:
                for series in study["series"]:
                    if series["SeriesInstanceUID"] == series_uid:
                        # Transform to DICOMweb format
                        dicomweb_instances = []
                        for instance in series["instances"]:
                            metadata = instance["metadata"]
                            dicomweb_instance = {
                                "00080018": {"vr": "UI", "Value": [metadata["SOPInstanceUID"]]},
                                "0020000D": {"vr": "UI", "Value": [study["StudyInstanceUID"]]},
                                "0020000E": {"vr": "UI", "Value": [series["SeriesInstanceUID"]]},
                                "00200013": {"vr": "IS", "Value": [metadata["InstanceNumber"]]}
                            }
                            dicomweb_instances.append(dicomweb_instance)
                        
                        return jsonify(dicomweb_instances)
        
        return jsonify({"error": "Series not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dicomweb/studies/<study_uid>/series/<series_uid>/instances/<instance_uid>', methods=['GET'])
async def dicomweb_instance(study_uid: str, series_uid: str, instance_uid: str):
    """DICOMweb compatible instance endpoint"""
    try:
        studies_data = await dicom_service._scan_dicom_files()
        for study in studies_data["studies"]:
            if study["StudyInstanceUID"] == study_uid:
                for series in study["series"]:
                    if series["SeriesInstanceUID"] == series_uid:
                        for instance in series["instances"]:
                            if instance["metadata"]["SOPInstanceUID"] == instance_uid:
                                # Extract filename from URL
                                url = instance["url"]
                                filename = url.split("/")[-1]
                                file_path = None
                                
                                for path in DICOM_DIR.rglob("*.dcm"):
                                    if path.name == filename:
                                        file_path = path
                                        break
                                
                                if not file_path:
                                    return jsonify({"error": "File not found"}), 404
                                
                                # Return DICOM file with proper content type
                                return await send_file(
                                    str(file_path),
                                    mimetype='application/dicom'
                                )
        
        return jsonify({"error": "Instance not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
async def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Create DICOM directory if it doesn't exist
    DICOM_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting DICOM server with files from: {DICOM_DIR}")
    print("Available endpoints:")
    print("  GET /api/studies - Get all studies")
    print("  GET /api/studies/<study_uid> - Get specific study")
    print("  GET /api/series/<series_uid> - Get specific series")
    print("  GET /dicom/file/<filename> - Get DICOM file")
    print("  GET /dicomweb/studies - DICOMweb studies endpoint")
    print("  GET /health - Health check")
    
    app.run(host='0.0.0.0', port=5000, debug=True)