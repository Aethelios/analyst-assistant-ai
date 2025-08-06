

from src.rag_pipeline import RAGPipeline

def run_retriever_test():
    """
    Initializes the RAG pipeline and tests the retriever function.
    """
    rag_pipe = RAGPipeline()

    test_query = "Which customer lives in Panama?" 

    print(f"--- Testing Retriever with query: '{test_query}' ---")

    documents, metadatas = rag_pipe.retrieve_chunks(test_query)

    if not documents:
        print("No documents were retrieved. The database might be empty or the query irrelevant.")
        return
        
    print("\n--- Retrieved Documents ---")
    for i, (doc, meta) in enumerate(zip(documents, metadatas)):
        print(f"\n[Chunk {i+1}]")
        print(f"Source: {meta.get('source', 'N/A')}")
        print(f"Content: {doc}")
        print("-" * 20)

if __name__ == "__main__":
    run_retriever_test()