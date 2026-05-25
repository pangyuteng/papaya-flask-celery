# DICOM Viewer with OHIF Frontend and Quart Backend

A comprehensive DICOM viewer solution built with:
- **Frontend**: OHIF Viewers for advanced medical image visualization
- **Backend**: Python Quart with async DICOM file serving
- **Deployment**: Docker containers with docker-compose orchestration

## Features

- 🏥 Medical-grade DICOM viewer with 3 orthogonal views (axial, sagittal, coronal)
- 🔄 Multiplanar Reconstruction (MPR) and 3D volume rendering
- 🚀 Asynchronous backend for high-performance DICOM file serving
- 🐳 Docker-based deployment for easy setup and scaling
- 🌐 RESTful API with DICOMweb compatibility
- 📱 Responsive web interface for desktop and mobile

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OHIF Frontend │◄──►│  Quart Backend  │◄──►│   DICOM Files   │
│   (Port 3000)   │    │  (Port 5000)    │    │   (Volume)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- DICOM files (optional for testing)

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd ohif-viewer
```

2. Add your DICOM files to the `dicom_files/` directory:
```bash
# Copy your DICOM files
cp /path/to/your/dicom/files/* dicom_files/
```

3. Build and start the containers:
```bash
docker-compose up --build
```

4. Access the viewer:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## Usage

### Viewing DICOM Studies

1. Open http://localhost:3000 in your browser
2. The OHIF viewer will load and connect to the backend
3. Studies will be automatically discovered from the `dicom_files/` directory
4. Select a study to view in 3 orthogonal views

### Available Views

- **Axial View**: Top-down view of the anatomy
- **Sagittal View**: Side view of the anatomy  
- **Coronal View**: Front view of the anatomy
- **3D Volume Rendering**: Interactive 3D visualization

### API Endpoints

#### REST API
- `GET /api/studies` - List all studies
- `GET /api/studies/{study_uid}` - Get specific study
- `GET /api/series/{series_uid}` - Get specific series
- `GET /dicom/file/{filename}` - Download DICOM file

#### DICOMweb Compatible
- `GET /dicomweb/studies` - QIDO-RS studies
- `GET /dicomweb/studies/{study_uid}` - QIDO-RS series
- `GET /dicomweb/studies/{study_uid}/series/{series_uid}/instances` - QIDO-RS instances
- `GET /dicomweb/studies/{study_uid}/series/{series_uid}/instances/{instance_uid}` - WADO-RS

## Configuration

### Frontend Configuration

Edit `frontend/config.js` to customize:
- Data source connections
- Default viewing modes
- Hanging protocols
- Extension settings

### Backend Configuration

The backend automatically discovers DICOM files in the `/app/dicom_files` directory. You can:

- Add/remove files by updating the volume mount
- Modify CORS settings in `backend/app.py`
- Adjust caching behavior

## Development

### Local Development

1. Install dependencies:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend (if building locally)
cd frontend
npm install
```

2. Run services:
```bash
# Backend
cd backend
python app.py

# Frontend (in separate terminal)
cd frontend
npm run dev
```

### File Structure

```
├── backend/
│   ├── app.py              # Main Quart application
│   ├── Dockerfile          # Backend Docker configuration
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── config.js          # OHIF configuration
│   ├── extensions.config.js # Extensions configuration
│   ├── nginx.conf         # Nginx configuration
│   └── Dockerfile         # Frontend Docker configuration
├── dicom_files/           # DICOM file storage
├── docker-compose.yml     # Container orchestration
└── README.md             # This file
```

## Troubleshooting

### Common Issues

1. **No studies visible**
   - Ensure DICOM files are in the `dicom_files/` directory
   - Check backend logs for file scanning errors
   - Verify files have `.dcm` extension

2. **CORS errors**
   - Check browser console for specific error messages
   - Verify backend CORS configuration
   - Ensure proper URL configuration in frontend config

3. **Performance issues**
   - For large studies, consider enabling compression
   - Monitor Docker resource usage
   - Optimize DICOM file organization

### Logs

View container logs:
```bash
docker-compose logs -f frontend
docker-compose logs -f backend
```

## Production Deployment

### Security Considerations

- Configure proper CORS policies
- Use HTTPS in production
- Implement authentication/authorization
- Secure DICOM file access

### Scaling

- Use Docker Swarm or Kubernetes for container orchestration
- Implement load balancing for multiple frontend instances
- Consider cloud storage for DICOM files

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Review Docker logs
- Open an issue on the repository