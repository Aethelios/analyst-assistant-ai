# notebooks/04_test_rag_chain.py
from src.rag_pipeline import RAGPipeline

def run_rag_test():
    """
    Initializes the RAG pipeline and tests the full answer generation.
    """
    # 1. Create an instance of the pipeline
    rag_pipe = RAGPipeline()
    chat_history = []

    
    # 2. Define a test query.
    #    Make sure this is a question your documents can answer!
    test_query = "Which customer lives in the country Panama?" #<-- CHANGE THIS QUERY based on your data

    print(f"--- Testing Full RAG Chain with query: '{test_query}' ---")
    
    # 3. Call the generate_answer method
    final_answer, sources, next_steps = rag_pipe.generate_answer(test_query)
    
    # 4. Print the final answer
    print("\n" + "="*50)
    print("Final Answer:")
    print(final_answer)
    print("="*50)

    if sources:
        print("\n--- Sources ---")
        # Use a set to only show unique source filenames
        unique_sources = {meta['source'] for meta in sources}
        for source_file in unique_sources:
            print(f"- {source_file}")
    else:
        print("\nNo sources found for this answer.")

    if next_steps:
        print("\n--- Suggested Next Steps ---")
        print(next_steps)
    else:
        print("\nNo next steps were generated.")

    print("="*50)
    query1 = "Which customer had the oldest subscription?" #<-- CHANGE
    print(f"\n--- Turn 1 Query: '{query1}' ---")
    answer1, sources1, next_steps1 = rag_pipe.generate_answer(query1, chat_history)
    print("\nAnswer:", answer1)
    print("\nSources:", {meta['source'] for meta in sources1})
    print("\nNext Steps:", next_steps1)
    chat_history.append((query1, answer1)) # Add to history

    # --- TURN 2 (Follow-up) ---
    query2 = "In which country do they live?" #<-- CHANGE
    print(f"\n--- Turn 2 Query (with history): '{query2}' ---")
    answer2, sources2, next_steps2 = rag_pipe.generate_answer(query2, chat_history)
    print("\nAnswer:", answer2)
    print("\nSources:", {meta['source'] for meta in sources2})

if __name__ == "__main__":
    run_rag_test()