
import os
from .parsers.pdf_parser import parse_pdf
from .parsers.docx_parser import parse_docx
from .parsers.txt_parser import parse_txt
from .parsers.csv_parser import parse_csv


PARSER_MAPPING = {
    '.pdf': parse_pdf,
    '.docx': parse_docx,
    '.txt': parse_txt,
    '.csv': parse_csv,
}

def load_document(file_path: str) -> str:
    """
    Loads a document from the given file path and returns its text content.
    It uses the file extension to determine which parser to use.
    """
    _, extension = os.path.splitext(file_path)
    
    if extension not in PARSER_MAPPING:
        raise ValueError(f"Unsupported file type: {extension}")
    
    parser = PARSER_MAPPING[extension]
    print(f"Parsing '{os.path.basename(file_path)}' with {parser.__name__}...")
    return parser(file_path)