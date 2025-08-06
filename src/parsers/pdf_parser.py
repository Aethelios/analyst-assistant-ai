# src/parsers/pdf_parser.py
import fitz  # PyMuPDF

def parse_pdf(file_path: str) -> str:
    """Extracts text content from a PDF file."""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error parsing PDF {file_path}: {e}")
        return ""