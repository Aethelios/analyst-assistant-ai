# src/parsers/txt_parser.py
def parse_txt(file_path: str) -> str:
    """Reads content from a TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error parsing TXT {file_path}: {e}")
        return ""