# src/ingestion_pipeline.py
import os
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
# The new, recommended import path
from langchain_huggingface import HuggingFaceEmbeddings
from .document_parser import load_document

# --- CONFIGURATION ---
CHROMA_DB_PATH = "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "analyst_assistant_collection"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

class IngestionPipeline:
    """A class to handle the document ingestion pipeline."""
    
    def __init__(self):
        self.db_client = None
        self.collection = None
        self.embedding_function = None
        self.text_splitter = None

    def _initialize(self):
        """Initializes all components of the pipeline. This is called on demand."""
        print("Initializing ingestion pipeline components...")
        
        # 1. Initialize ChromaDB client
        # This will create the directory if it doesn't exist
        self.db_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

        # 2. Get or create the collection
        self.collection = self.db_client.get_or_create_collection(name=COLLECTION_NAME)

        # 3. Initialize the embedding model
        self.embedding_function = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'} # Use 'cuda' if you have a GPU
        )

        # 4. Initialize the text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len
        )
        print("Initialization complete.")

    def ingest_file(self, file_path: str):
        """
        The main ingestion pipeline function for a single file.
        """
        # Ensure components are initialized before proceeding
        if self.collection is None:
            self._initialize()

        print(f"--- Starting ingestion for {file_path} ---")
        
        # Load document content
        text_content = load_document(file_path)
        if not text_content:
            print(f"No content extracted from {file_path}. Skipping.")
            return

        # Chunk the text
        print("Splitting text into chunks...")
        chunks = self.text_splitter.split_text(text_content)
        
        # Create unique IDs for each chunk
        ids = [f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
        
        # Create embeddings (this is done by ChromaDB automatically when adding)
        print(f"Storing {len(chunks)} chunks in ChromaDB...")
        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=[{'source': os.path.basename(file_path)} for _ in ids]
        )
        
        print(f"--- Ingestion complete for {file_path} ---")

# Optional: Add a function to get the collection for verification purposes
def get_db_collection():
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return client.get_collection(name=COLLECTION_NAME)