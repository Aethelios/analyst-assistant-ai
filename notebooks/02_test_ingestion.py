import os
import shutil
from src.ingestion_pipeline import IngestionPipeline, get_db_collection, CHROMA_DB_PATH

TEST_DATA_DIR = "data"
TEST_FILES = {
    "txt": os.path.join(TEST_DATA_DIR, "sample.txt"),
    "csv": os.path.join(TEST_DATA_DIR, "sample.csv"),
    "txt": os.path.join(TEST_DATA_DIR, "story.txt"),
    # Add paths for a sample PDF and DOCX once you have them
}

def run_ingestion_test():
    """
    Cleans up old database, runs ingestion on test files, and verifies the result.
    """
    if os.path.exists(CHROMA_DB_PATH):
        print(f"Removing old database at {CHROMA_DB_PATH}...")
        shutil.rmtree(CHROMA_DB_PATH)

    pipeline = IngestionPipeline()

    for file_type, file_path in TEST_FILES.items():
        if os.path.exists(file_path):
            pipeline.ingest_file(file_path)
        else:
            print(f"Warning: Test file not found at {file_path}. Skipping.")
            
    try:
        collection = get_db_collection()
        count = collection.count()
        print(f"\nVerification: Found {count} documents in the database.")
        
        if count > 0:
            print("\nPeeking at one of the stored documents:")
            print(collection.peek(limit=1))
    except Exception as e:
        print(f"Could not verify database contents: {e}")


if __name__ == "__main__":
    run_ingestion_test()