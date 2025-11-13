# Quick Start Guide

Get the MarkItDown API up and running in 3 minutes!

## Prerequisites

- Python 3.8 or higher
- pip package manager
- **For OCR support (scanned PDFs):**
  - Tesseract OCR
  - Poppler utils

## Installation Steps

### 1. Clone and Navigate
```bash
git clone https://github.com/PetengDedet/markitdown-api.git
cd markitdown-api
```

### 2. Install System Dependencies (for OCR)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

**Windows:**
- Download [Tesseract OCR installer](https://github.com/UB-Mannheim/tesseract/wiki)
- Download [Poppler for Windows](https://blog.alivate.com.au/poppler-windows/)

*Note: Skip this step if you only need to process text-based PDFs and other document formats.*

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

### 5. Access the Application

Open your browser and go to: **http://localhost:5000**

### 6. Login

Use the default credentials:
- **Username**: `admin`
- **Password**: `admin`

⚠️ **Important**: Change these credentials immediately via the Settings page!

## First Steps

### Upload Your First Document

1. Click **"Upload"** in the navigation bar
2. **Select Analysis Features**: Choose which features to apply using the checkboxes:
   - ✅ **Title Prediction** - Generate a suggested title
   - ✅ **Markdown Extraction** - Extract markdown content
   - ✅ **Document Categorization** - Classify into categories
   - ✅ **Keyword Extraction** - Extract key terms
   - ✅ **Severity Classification** - Determine importance level
   - ✅ **Summarization** - Generate summary (requires LLM)
   - ✅ **Correction** - Fix spelling/grammar (requires LLM)
3. Drag a document file or click to browse
4. Click **"Convert to Markdown"**
5. View the conversion result with all selected features in the chat interface!

**Note**: All features except Summarization and Correction work locally without additional setup. For LLM-powered features, see the [LLM Setup Guide](LLM_SETUP.md).

### View Conversion History

Click **"Recent Conversions"** to see all your converted documents in a table.

### Configure Settings

Go to **"Settings"** to:
- Change your username and password
- Modify allowed file extensions
- Adjust maximum file size

## Supported File Types

By default, the application supports:
- PDF documents (`.pdf`) - **including scanned PDFs with OCR**
- Word documents (`.docx`, `.doc`)
- Text files (`.txt`)
- HTML files (`.html`, `.htm`)
- PowerPoint (`.pptx`)
- Excel (`.xlsx`)

**OCR Feature**: The application automatically detects scanned PDFs (image-only) and uses OCR to extract text. No special action is needed - just upload your scanned PDF and it will be processed automatically!

You can modify these in the Settings page.

## API Usage

### Authentication

First, login to get a session cookie:
```bash
curl -c cookies.txt -X POST http://localhost:5000/login \
  -d "username=admin&password=admin"
```

### Convert a Document with Feature Selection

```bash
# Convert with specific features
curl -b cookies.txt -X POST http://localhost:5000/api/convert \
  -F "file=@document.pdf" \
  -F "features=title_prediction,document_categorization,keyword_extraction"

# Convert with all features (default if not specified)
curl -b cookies.txt -X POST http://localhost:5000/api/convert \
  -F "file=@document.pdf"
```

**Available Features:**
- `title_prediction` - Generate document title
- `markdown_extraction` - Extract markdown content
- `document_categorization` - Classify into categories
- `keyword_extraction` - Extract keywords
- `severity_classification` - Determine importance
- `summarization` - Generate summary (requires LLM)
- `correction` - Fix spelling/grammar (requires LLM)

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
