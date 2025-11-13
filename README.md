# MarkItDown API

A Flask-based REST API and web interface for converting documents to Markdown format using the MarkItDown library, with advanced document analysis features.

## Features

### Core Features
- 📤 **File Upload & Conversion**: Upload documents (.docx, .pdf, .txt, etc.) and convert them to Markdown
- 🔍 **OCR Support**: Automatic OCR for scanned PDFs using Tesseract and pdf2image
- 🔐 **Authentication**: Secure login system with username/password protection
- ⚙️ **Configuration**: Web interface to manage app settings and credentials
- 📊 **Recent Conversions**: View history of all document conversions
- 💬 **Interactive Interface**: Chat-style UI for uploading and viewing conversion results
- 🗄️ **Database Storage**: SQLite database for persistent storage of conversions and metadata

### Advanced Document Analysis Features (NEW!)
Select from multiple analysis options for each document:

- 📝 **Title Prediction**: Automatically generate a suggested title for uploaded documents
  - Uses LLM-based generation when available, with smart heuristic fallback
  
- 📄 **Markdown Extraction**: Extract clean Markdown content from various document formats
  - Supports .docx, .pdf, .txt, .html, .pptx, .xlsx, and more
  
- 🏷️ **Document Categorization**: Predict document categories using keyword-based classification
  - Multi-label classification supporting Business, Technical, Legal, Financial, etc.
  - Confidence scores for each predicted category
  
- 🔑 **Keyword Extraction**: Extract representative keywords to improve searchability
  - Frequency-based analysis with stop word filtering
  - Supports both English and Bahasa Indonesia
  
- ⚡ **Severity Classification**: Predict document importance level
  - Classifies as Critical, Important, Normal, or Low Priority
  - Based on keyword analysis and content patterns
  
- 📊 **Summarization**: Generate concise summaries (requires LLM)
  - Uses local Qwen1.5-1.8B model for AI-powered summarization
  - Optimized for Bahasa Indonesia and English
  
- ✅ **Correction**: Automatically correct spelling, grammar, and formatting (requires LLM)
  - Spell-check and grammar correction
  - Markdown reformatting for better readability

All features run **100% locally** with no external API calls required!

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Tesseract OCR (for scanned PDF support)
- Poppler utils (for PDF to image conversion)

### System Dependencies

For OCR support with scanned PDFs, install the following system packages:

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
- Download and install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- Download and install [Poppler for Windows](https://blog.alivate.com.au/poppler-windows/)

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

## Using Document Analysis Features

### Web Interface

1. **Upload a Document**: Navigate to the Upload page and choose a file
2. **Select Features**: Use the checkboxes to select which analysis features to apply:
   - ✅ Title Prediction - Generate a document title
   - ✅ Markdown Extraction - Extract markdown content (always enabled)
   - ✅ Document Categorization - Classify document into categories
   - ✅ Keyword Extraction - Extract important keywords
   - ✅ Severity Classification - Determine document importance
   - ✅ Summarization - Generate AI summary (requires LLM)
   - ✅ Correction - Fix spelling/grammar (requires LLM)
3. **Convert**: Click "Convert to Markdown" to process the document
4. **View Results**: Results are displayed with visual indicators for each feature

### REST API

Use the `/api/convert` endpoint with feature selection:

```bash
curl -X POST http://localhost:5000/api/convert \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@document.pdf" \
  -F "features=title_prediction,document_categorization,keyword_extraction"
```

**Available feature values:**
- `title_prediction` - Generate title
- `markdown_extraction` - Extract markdown
- `document_categorization` - Classify categories
- `keyword_extraction` - Extract keywords
- `severity_classification` - Classify severity
- `summarization` - Generate summary (requires LLM)
- `correction` - Correct text (requires LLM)

**Response format:**
```json
{
  "success": true,
  "id": 1,
  "filename": "document.pdf",
  "predicted_title": "Business Proposal for Q4 2024",
  "categories": [
    {"category": "Business", "confidence": 0.95},
    {"category": "Proposal", "confidence": 0.82}
  ],
  "keywords": ["business", "proposal", "strategy", "revenue"],
  "severity": "Important",
  "markdown_content": "# Document content...",
  "summary_content": "AI-generated summary...",
  "corrected_content": "Corrected markdown..."
}
```

**Note:** If no features are specified, all available features are applied by default.

## LLM-Powered Document Processing (Optional)

MarkItDown API now supports **local AI processing** for document summarization and correction using the Qwen1.5-1.8B model. This feature:

- ✅ Corrects spelling and grammar (optimized for **Bahasa Indonesia** and English)
- ✅ Reformats markdown for better readability  
- ✅ Summarizes content into concise paragraphs
- ✅ Runs **100% locally** - no external API calls
- ✅ Uses quantized models for efficient resource usage (~1GB model, ~3GB RAM)

### Quick Setup

**For new installations:**

1. Download the Qwen1.5-1.8B quantized model:
```bash
mkdir -p models
wget https://huggingface.co/Qwen/Qwen1.5-1.8B-Chat-GGUF/resolve/main/qwen1_5-1_8b-chat-q4_k_m.gguf -O models/qwen1.5-1.8b-q4_k_m.gguf
```

2. Enable LLM processing in the Settings page of the web interface

3. Configure options (task type, max tokens, temperature)

**For upgrading existing installations:**

1. Run the database migration script first:
```bash
python migrate_db.py
```

2. Then follow steps 1-3 above

**For detailed instructions**, see [LLM_SETUP.md](LLM_SETUP.md)

**Note**: LLM processing is optional and disabled by default. The application works normally without it.

## OCR Support for Scanned PDFs

The application now includes automatic OCR (Optical Character Recognition) support for scanned PDFs. When you upload a PDF:

1. **Text-based PDFs**: Regular PDFs with extractable text are processed using the standard MarkItDown library
2. **Scanned PDFs**: PDFs without extractable text (image-only) are automatically processed using OCR:
   - Each page is converted to an image using pdf2image
   - Text is extracted from images using Tesseract OCR
   - Extracted text is organized by page and converted to Markdown format

The system automatically detects whether a PDF needs OCR processing, so you don't need to do anything special. Just upload your PDF and the application will handle it appropriately.

**Note**: OCR processing may take longer than regular text extraction, especially for large documents or high-resolution scans.

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
- file: Document file to convert (required)
- features: Comma-separated list of features to apply (optional)
  Available: title_prediction, markdown_extraction, document_categorization,
            keyword_extraction, severity_classification, summarization, correction

Example:
curl -X POST http://localhost:5000/api/convert \
  -F "file=@document.pdf" \
  -F "features=title_prediction,document_categorization,keyword_extraction"

Response:
{
    "success": true,
    "id": 1,
    "filename": "document.pdf",
    "predicted_title": "Business Report Q4 2024",
    "categories": [
        {"category": "Business", "confidence": 0.95},
        {"category": "Report", "confidence": 0.87}
    ],
    "keywords": ["business", "revenue", "strategy", "growth"],
    "severity": "Important",
    "markdown_content": "# Document content...",
    "summary_content": "AI-generated summary...",
    "corrected_content": "Corrected content...",
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
├── analysis_utils.py      # Document analysis utilities (NEW!)
├── llm_utils.py           # LLM processing utilities
├── ocr_utils.py           # OCR utility functions for scanned PDFs
├── migrate_db.py          # Database migration script
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

### Python Packages
- Flask 3.0.0 - Web framework
- markitdown 0.0.1a2 - Document to Markdown conversion
- SQLAlchemy 2.0.23 - Database ORM
- Flask-Login 0.6.3 - User authentication
- Werkzeug 3.0.3 - Password hashing and utilities
- pdf2image 1.16.3 - PDF to image conversion for OCR
- pytesseract 0.3.10 - Python wrapper for Tesseract OCR
- llama-cpp-python 0.2.90 - Local LLM inference (optional, for Qwen1.5-1.8B)

### System Dependencies
- Tesseract OCR - Optical Character Recognition engine for scanned PDFs
- Poppler utils - PDF rendering library for image conversion

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
