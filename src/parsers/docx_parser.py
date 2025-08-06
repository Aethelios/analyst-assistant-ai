# src/parsers/docx_parser.py
import docx

def parse_docx(file_path: str) -> str:
    """Extracts text content from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error parsing DOCX {file_path}: {e}")
        return ""