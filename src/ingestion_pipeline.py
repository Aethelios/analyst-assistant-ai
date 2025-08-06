import os
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
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
        

        self.db_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

        self.collection = self.db_client.get_or_create_collection(name=COLLECTION_NAME)

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

        if self.collection is None:
            self._initialize()

        print(f"--- Starting ingestion for {file_path} ---")
        

        text_content = load_document(file_path)
        if not text_content:
            print(f"No content extracted from {file_path}. Skipping.")
            return


        print("Splitting text into chunks...")
        chunks = self.text_splitter.split_text(text_content)
        

        ids = [f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
        

        print(f"Storing {len(chunks)} chunks in ChromaDB...")
        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=[{'source': os.path.basename(file_path)} for _ in ids]
        )
        
        print(f"--- Ingestion complete for {file_path} ---")


def get_db_collection():
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return client.get_collection(name=COLLECTION_NAME)