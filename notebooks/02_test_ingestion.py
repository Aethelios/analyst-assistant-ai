# notebooks/02_test_ingestion.py
import os
import shutil
# Import the class and the helper function
from src.ingestion_pipeline import IngestionPipeline, get_db_collection, CHROMA_DB_PATH

# Define paths for our test files
TEST_DATA_DIR = "data"
TEST_FILES = {
    "txt": os.path.join(TEST_DATA_DIR, "sample.txt"),
    "csv": os.path.join(TEST_DATA_DIR, "sample.csv"),
    # Add paths for a sample PDF and DOCX once you have them
}

def run_ingestion_test():
    """
    Cleans up old database, runs ingestion on test files, and verifies the result.
    """
    # 1. Clean up any previous database instance
    # This now works because no process has a lock on the files yet.
    if os.path.exists(CHROMA_DB_PATH):
        print(f"Removing old database at {CHROMA_DB_PATH}...")
        shutil.rmtree(CHROMA_DB_PATH)

    # 2. Create an instance of the pipeline
    pipeline = IngestionPipeline()

    # 3. Run ingestion for each test file
    for file_type, file_path in TEST_FILES.items():
        if os.path.exists(file_path):
            # The first time this is called, it will initialize the DB
            pipeline.ingest_file(file_path)
        else:
            print(f"Warning: Test file not found at {file_path}. Skipping.")
            
    # 4. Verify the content in the database
    # Now we connect to the DB *after* all writing is done
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