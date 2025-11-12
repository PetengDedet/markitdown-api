# Quick Start Guide

Get the MarkItDown API up and running in 3 minutes!

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Installation Steps

### 1. Clone and Navigate
```bash
git clone https://github.com/PetengDedet/markitdown-api.git
cd markitdown-api
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

### 4. Access the Application

Open your browser and go to: **http://localhost:5000**

### 5. Login

Use the default credentials:
- **Username**: `admin`
- **Password**: `admin`

⚠️ **Important**: Change these credentials immediately via the Settings page!

## First Steps

### Upload Your First Document

1. Click **"Upload"** in the navigation bar
2. Drag a document file or click to browse
3. Click **"Convert to Markdown"**
4. View the conversion result in the chat interface!

### View Conversion History

Click **"Recent Conversions"** to see all your converted documents in a table.

### Configure Settings

Go to **"Settings"** to:
- Change your username and password
- Modify allowed file extensions
- Adjust maximum file size

## Supported File Types

By default, the application supports:
- PDF documents (`.pdf`)
- Word documents (`.docx`, `.doc`)
- Text files (`.txt`)
- HTML files (`.html`, `.htm`)
- PowerPoint (`.pptx`)
- Excel (`.xlsx`)

You can modify these in the Settings page.

## API Usage

### Authentication

First, login to get a session cookie:
```bash
curl -c cookies.txt -X POST http://localhost:5000/login \
  -d "username=admin&password=admin"
```

### Convert a Document

```bash
curl -b cookies.txt -X POST http://localhost:5000/api/convert \
  -F "file=@document.pdf"
```

### List Conversions

```bash
curl -b cookies.txt http://localhost:5000/api/conversions
```

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify the last line in `app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=8080)  # Change port number
```

### Database Errors
If you encounter database errors, delete `markitdown.db` and restart the application. A fresh database will be created automatically.

### Import Errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [SECURITY.md](SECURITY.md) for security best practices
- Explore the REST API endpoints
- Customize the application for your needs

## Need Help?

Check the logs in the terminal where you started the application. The application logs all errors and important events.

For production deployment, refer to the README.md file for recommendations on using WSGI servers and HTTPS.

---

**Enjoy using MarkItDown API!** 🚀
