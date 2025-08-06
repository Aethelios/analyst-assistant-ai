import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from ctransformers import AutoModelForCausalLM

# --- CONFIGURATION ---
CHROMA_DB_PATH = "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "analyst_assistant_collection"
# LLM_MODEL_PATH = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
LLM_MODEL_PATH = "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

QA_PROMPT_TEMPLATE = """
### Instruction:
You are a helpful AI assistant for data analysis. Use the following retrieved context to answer the user's question.
If you don't know the answer, just say that you don't know. Don't try to make up an answer.
Provide a concise and factual answer based *only* on the provided context.

### Context:
{context}

### User's Question:
{question}

### Answer:
"""

SUMMARY_PROMPT_TEMPLATE = """
### Instruction:
You are an expert summarizer. Your task is to create a concise summary of the following text, which is a chunk from a larger document.
Focus on the key facts, figures, and main topics.

### Context:
{context}

### Summary of this chunk:
"""

NEXT_STEPS_PROMPT_TEMPLATE = """
### Instruction:
You are a helpful AI analyst. Based on the user's original question and the answer provided, suggest 3 relevant, insightful, and actionable follow-up questions that the user might want to ask. The questions should be directly answerable from the context of a financial or data analysis document. Present them as a numbered list. Do not add any extra text or commentary.

### Original Question:
{question}

### Provided Answer:
{answer}

### Suggested Follow-up Questions:
"""

class RAGPipeline:
    def __init__(self):
        self.db_client = None
        self.collection = None
        self.embedding_function = None
        self.llm = None
        self.prompt = None

    def _initialize(self):
        """Initializes the database client and embedding function."""
        if self.collection is None:
            print("Initializing RAG pipeline components...")
            self.db_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
            self.collection = self.db_client.get_collection(name=COLLECTION_NAME)
            
            self.embedding_function = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'} # Use 'cuda' if you have a GPU
            )
            print("Loading local LLM...")

            self.llm = AutoModelForCausalLM.from_pretrained(
                LLM_MODEL_PATH,
                #model_type="mistral",
                model_type="llama",
                gpu_layers=1,  # Set to a value > 0 if you have a supported GPU
                temperature=0.1,
                max_new_tokens=512,
                context_length=4096 
            )
            print("LLM loaded.")
            
            # Create the prompt from the template
            self.prompt = PromptTemplate(
                template=QA_PROMPT_TEMPLATE,
                input_variables=['context', 'question']
            )
            self.next_steps_prompt = PromptTemplate(
                template=NEXT_STEPS_PROMPT_TEMPLATE,
                input_variables=['question', 'answer']
            )

            print("RAG components initialized.")

    def retrieve_chunks(self, query: str, top_k: int = 5):
        """
        Retrieves the top_k most relevant chunks from the database.
        """
        self._initialize()

        print(f"Retrieving top {top_k} relevant chunks for query: '{query}'")
        
        query_embedding = self.embedding_function.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        
        retrieved_docs = results['documents'][0]
        retrieved_metadatas = results['metadatas'][0]

        print(f"Found {len(retrieved_docs)} relevant chunks.")
        
        return retrieved_docs, retrieved_metadatas
    

    def generate_answer(self, query: str, chat_history: list = []):
        """
        The main RAG chain function.
        1. Retrieves relevant context.
        2. Formats the prompt.
        3. Generates an answer with the LLM.
        4. Returns the answer and the source documents.
        """

        self._initialize()

        full_query = query
        if chat_history:
            # Add the last Q&A pair to the query for context
            last_question, last_answer = chat_history[-1]
            full_query = f"Considering the previous question was '{last_question}', now answer this: {query}"

        # 1. Retrieve context
        retrieved_docs, retrieved_metadatas = self.retrieve_chunks(full_query)
        
        # Check if any context was retrieved
        if not retrieved_docs:
            print("No relevant context found. Cannot generate answer.")
            return "I could not find any relevant information in the uploaded documents to answer your question."

        # 2. Format the context for the prompt
        # We'll join the documents together with a clear separator.
        context_str = "\n\n---\n\n".join(retrieved_docs)

        # 3. Format the final prompt
        formatted_prompt = self.prompt.format(context=context_str, question=query)
        
        # 4. Generate the answer
        print("Generating answer...")
        response = self.llm(formatted_prompt)
         # --- NEW: GENERATE NEXT STEPS ---
        print("Generating next step suggestions...")
        next_steps_formatted_prompt = self.next_steps_prompt.format(
            question=query,
            answer=response
        )
        next_steps = self.llm(next_steps_formatted_prompt)
        print("Answer generation complete. Returning response and sources.")

        return response, retrieved_metadatas, next_steps
    
    def summarize_document(self, source_filename: str):
        """
        Summarizes the content of a specific document stored in the database.
        """
        self._initialize()

        print(f"Attempting to summarize document: {source_filename}")

        # Use ChromaDB's 'where' filter to get all chunks for a specific file
        # Note: The value in the where filter must match the metadata value exactly.
        results = self.collection.get(where={"source": source_filename})
        
        all_docs = results['documents']

        if not all_docs:
            return f"Could not find a document named '{source_filename}' in the database."

        # Join all chunks into a single text block
        full_text = "\n".join(all_docs)

        # Check if the text is too long for the context window
        # (A simple check, can be improved with a proper tokenizer later)
        if len(full_text) > (self.llm.config.context_length * 3): # Approx 3 chars per token
             return "The document is too large to summarize with the current method."

        # A new, simple prompt for one-shot summarization
        summary_prompt = f"""
            ### Instruction:
            You are a helpful AI assistant. Based on the following document text, please provide a concise, bullet-point summary of its key contents.

            ### Document Text:
            {full_text}

            ### Summary:
            """
        print("Generating summary...")
        summary = self.llm(summary_prompt)
        
        return summary