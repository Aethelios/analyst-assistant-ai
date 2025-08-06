# src/parsers/csv_parser.py
import pandas as pd

def parse_csv(file_path: str) -> str:
    """
    Parses a CSV file, converting each row into a human-readable sentence.
    This helps the LLM understand the tabular data contextually.
    """
    try:
        df = pd.read_csv(file_path)
        text_list = []
        for index, row in df.iterrows():
            row_text = ", ".join([f"{col} is {val}" for col, val in row.items()])
            text_list.append(f"Row {index + 1}: {row_text}.")
        return "\n".join(text_list)
    except Exception as e:
        print(f"Error parsing CSV {file_path}: {e}")
        return ""