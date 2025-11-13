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


def extract_text_from_scanned_pdf(pdf_path, dpi=300, max_pages=None):
    """
    Extract text from a scanned PDF using OCR.
    
    Args:
        pdf_path: Path to the scanned PDF file
        dpi: DPI for image conversion (default: 300)
        max_pages: Maximum number of pages to process (default: None for all pages)
        
    Returns:
        str: Extracted text from all pages
    """
    try:
        # Convert PDF pages to images
        images = convert_from_path(pdf_path, dpi=dpi)
        
        # Limit pages if specified
        if max_pages and len(images) > max_pages:
            images = images[:max_pages]
            pages_info = f"*Processing first {max_pages} of {len(convert_from_path(pdf_path, dpi=dpi))} pages*\n\n"
        else:
            pages_info = ""
        
        # Extract text from each page
        text_parts = []
        for i, image in enumerate(images):
            # Perform OCR on the image
            text = pytesseract.image_to_string(image)
            if text.strip():
                text_parts.append(f"## Page {i + 1}\n\n{text.strip()}")
        
        # Combine all pages
        if text_parts:
            return pages_info + "\n\n---\n\n".join(text_parts)
        else:
            return "No text could be extracted from the PDF."
            
    except Exception as e:
        raise Exception(f"OCR extraction failed: {str(e)}")


def convert_pdf_with_ocr_fallback(pdf_path, markitdown_converter, max_pages=None):
    """
    Convert PDF to markdown, using OCR if the PDF doesn't contain text.
    
    Args:
        pdf_path: Path to the PDF file
        markitdown_converter: MarkItDown instance
        max_pages: Maximum number of pages to OCR (default: None for all pages)
        
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
        ocr_text = extract_text_from_scanned_pdf(pdf_path, max_pages=max_pages)
        # Add a header to indicate OCR was used
        return f"*Text extracted using OCR*\n\n{ocr_text}"


def extract_text_from_image(image_path):
    """
    Extract text from an image using OCR and convert to markdown.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        str: Extracted text in markdown format
    """
    try:
        # Open the image
        image = Image.open(image_path)
        
        # Perform OCR on the image
        text = pytesseract.image_to_string(image)
        
        if text.strip():
            return f"*Text extracted from image using OCR*\n\n{text.strip()}"
        else:
            return "No text could be extracted from the image."
            
    except Exception as e:
        raise Exception(f"Image OCR failed: {str(e)}")
