from src.rag_pipeline import RAGPipeline

def run_summarizer_test():
    rag_pipe = RAGPipeline()
    
    # IMPORTANT: Change this to a filename that you have ingested
    # You can see the available filenames by running the previous test.
    test_filename = "story.txt" 

    print(f"--- Testing Summarizer for file: '{test_filename}' ---")
    
    summary = rag_pipe.summarize_document(test_filename)
    
    print("\n" + "="*50)
    print("Generated Summary:")
    print(summary)
    print("="*50)

if __name__ == "__main__":
    run_summarizer_test()