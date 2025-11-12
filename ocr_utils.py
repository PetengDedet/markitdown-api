"""OCR utility functions for handling scanned PDFs."""
import os
import tempfile
from pdf2image import convert_from_path
import pytesseract
from PIL import Image


def has_text_in_pdf(pdf_path):
    """
    Check if a PDF contains extractable text.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        bool: True if PDF contains text, False otherwise
    """
    try:
        # Try to extract text using pdfminer
        from pdfminer.high_level import extract_text
        text = extract_text(pdf_path)
        # Consider PDF as having text if there's more than whitespace
        return bool(text and text.strip())
    except Exception:
        # If we can't determine, assume it has text and let markitdown handle it
        return True


def extract_text_from_scanned_pdf(pdf_path, dpi=300):
    """
    Extract text from a scanned PDF using OCR.
    
    Args:
        pdf_path: Path to the scanned PDF file
        dpi: DPI for image conversion (default: 300)
        
    Returns:
        str: Extracted text from all pages
    """
    try:
        # Convert PDF pages to images
        images = convert_from_path(pdf_path, dpi=dpi)
        
        # Extract text from each page
        text_parts = []
        for i, image in enumerate(images):
            # Perform OCR on the image
            text = pytesseract.image_to_string(image)
            if text.strip():
                text_parts.append(f"## Page {i + 1}\n\n{text.strip()}")
        
        # Combine all pages
        if text_parts:
            return "\n\n---\n\n".join(text_parts)
        else:
            return "No text could be extracted from the PDF."
            
    except Exception as e:
        raise Exception(f"OCR extraction failed: {str(e)}")


def convert_pdf_with_ocr_fallback(pdf_path, markitdown_converter):
    """
    Convert PDF to markdown, using OCR if the PDF doesn't contain text.
    
    Args:
        pdf_path: Path to the PDF file
        markitdown_converter: MarkItDown instance
        
    Returns:
        str: Markdown content
    """
    # First, check if PDF has extractable text
    if has_text_in_pdf(pdf_path):
        # Use regular markitdown conversion
        result = markitdown_converter.convert(pdf_path)
        return result.text_content
    else:
        # Use OCR for scanned PDFs
        ocr_text = extract_text_from_scanned_pdf(pdf_path)
        # Add a header to indicate OCR was used
        return f"*Text extracted using OCR*\n\n{ocr_text}"
