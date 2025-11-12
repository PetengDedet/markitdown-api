# MarkItDown API

A Flask-based REST API and web interface for converting documents to Markdown format using the MarkItDown library.

## Features

- 📤 **File Upload & Conversion**: Upload documents (.docx, .pdf, .txt, etc.) and convert them to Markdown
- 🔐 **Authentication**: Secure login system with username/password protection
- ⚙️ **Configuration**: Web interface to manage app settings and credentials
- 📊 **Recent Conversions**: View history of all document conversions
- 💬 **Interactive Interface**: Chat-style UI for uploading and viewing conversion results
- 🗄️ **Database Storage**: SQLite database for persistent storage of conversions and metadata

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd markitdown-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The application will start on `http://localhost:5000`

## Default Credentials

- Username: `admin`
- Password: `admin`

**Important**: Change these credentials after first login via the Settings page.

## Usage

### Web Interface

1. **Login**: Navigate to `http://localhost:5000` and log in with default credentials
2. **Upload Documents**: Go to the Upload page to convert documents to Markdown
3. **View History**: Check the Recent Conversions page to see past conversions
4. **Configure**: Use the Settings page to change credentials and app configuration

### REST API Endpoints

#### Convert Document
```bash
POST /api/convert
Content-Type: multipart/form-data

Parameters:
- file: Document file to convert

Response:
{
    "success": true,
    "id": 1,
    "filename": "document.pdf",
    "markdown_content": "# Document content...",
    "upload_time": "2024-01-01T12:00:00",
    "file_size": 1024
}
```

#### Get Conversions List
```bash
GET /api/conversions?limit=50

Response:
{
    "conversions": [
        {
            "id": 1,
            "filename": "document.pdf",
            "markdown_content": "...",
            "upload_time": "2024-01-01T12:00:00",
            "file_size": 1024
        }
    ]
}
```

#### Get Specific Conversion
```bash
GET /api/conversion/<id>

Response:
{
    "id": 1,
    "filename": "document.pdf",
    "markdown_content": "...",
    "upload_time": "2024-01-01T12:00:00",
    "file_size": 1024
}
```

## Project Structure

```
markitdown-api/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── config.html
│   ├── recent.html
│   └── upload.html
├── static/                # Static assets
│   └── css/
│       └── style.css
└── uploads/               # Uploaded files storage
```

## Configuration

Application settings can be modified through the web interface or directly in the database:

- **Allowed File Extensions**: Comma-separated list of allowed file extensions
- **Max File Size**: Maximum file size in bytes
- **Username/Password**: Admin credentials

## Security Notes

1. Change default credentials immediately after first login
2. Use environment variable `SECRET_KEY` in production
3. Consider using HTTPS in production environments
4. Regularly backup the database file

## Dependencies

- Flask 3.0.0 - Web framework
- markitdown 0.0.1a2 - Document to Markdown conversion
- SQLAlchemy 2.0.23 - Database ORM
- Flask-Login 0.6.3 - User authentication
- Werkzeug 3.0.1 - Password hashing and utilities

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
