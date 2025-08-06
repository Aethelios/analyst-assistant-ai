import os
import shutil

# The path to your ChromaDB database directory
DB_PATH = "chroma_db"

def clear_database():
    """
    Deletes the ChromaDB database directory to clear all stored data.
    """
    if os.path.exists(DB_PATH):
        print(f"Found database at '{DB_PATH}'. Deleting...")
        try:
            shutil.rmtree(DB_PATH)
            print("Database cleared successfully.")
        except OSError as e:
            print(f"Error: {e.filename} - {e.strerror}.")
            print("Please ensure no other processes are using the database and try again.")
    else:
        print("Database not found. Nothing to clear.")

if __name__ == "__main__":
    # Ask for confirmation to prevent accidental deletion
    confirm = input(f"Are you sure you want to permanently delete the database at '{DB_PATH}'? (y/N): ")
    if confirm.lower() == 'y':
        clear_database()
    else:
        print("Operation cancelled.")