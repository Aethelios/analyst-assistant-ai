import streamlit as st
import os
import time
import sys

# --- Add the project root to the Python path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Now we can import from src
from src.ingestion_pipeline import IngestionPipeline
from src.rag_pipeline import RAGPipeline
from src.chart_generator import is_json, create_chart
from clear_database import clear_database

# --- Constants ---
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- Initialize session state (consolidated) ---
if "ingestion_done" not in st.session_state:
    st.session_state.ingestion_done = False
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = RAGPipeline()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_filename" not in st.session_state:
    st.session_state.processed_filename = None

# Set the page configuration
st.set_page_config(
    page_title="LLM Analyst Assistant",
    page_icon="🤖",
    layout="wide"
)

# App title
st.title("🤖 LLM-Powered Analyst Assistant")

def handle_query(prompt):
    """Handles the logic for a single user query."""
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Assistant's turn to respond
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            rag_pipe = st.session_state.rag_pipeline
            
            # Format chat history for the backend
            chat_history_for_backend = []
            for i, msg in enumerate(st.session_state.messages[:-1]):  # Exclude current question
                if msg["role"] == "user":
                    # Find the next assistant response
                    for j in range(i + 1, len(st.session_state.messages)):
                        if st.session_state.messages[j]["role"] == "assistant":
                            chat_history_for_backend.append((msg["content"], st.session_state.messages[j]["content"]))
                            break

            # Call the backend - the response might be text or JSON
            response, sources, next_steps = rag_pipe.generate_answer(
                query=prompt, 
                chat_history=chat_history_for_backend
            )
            
            # Check if the response is a chart or text
            is_chart_json, json_str = is_json(response)
            if is_chart_json:
                st.markdown("It looks like a chart is the best way to answer this. Generating visualization...")
                fig, err = create_chart(json_str)
                if err:
                    st.error(err)
                    # Show the raw JSON for debugging
                    st.code(json_str, language="json")
                else:
                    st.pyplot(fig)
                # Add a text confirmation to the chat history
                st.session_state.messages.append({"role": "assistant", "content": "[Chart generated above]"})
            else:
                # It's a regular text answer
                st.markdown(response)
                # Add the text answer to the message history
                st.session_state.messages.append({"role": "assistant", "content": response})

            # Display sources (this works for both chart and text answers)
            if sources:
                with st.expander("View Sources"):
                    for source in sources:
                        st.info(f"Source: {source.get('source', 'N/A')}")

            
            # Display next steps (this works for both chart and text answers)
            if next_steps:
                st.markdown("---")
                st.markdown("**Suggested Next Steps:**")
                # Parse the numbered list of questions
                questions = [q.strip() for q in next_steps.split('\n') if q.strip()]
                
                # Create buttons for each question
                for i, question in enumerate(questions):
                    # Remove the leading number and period (e.g., "1. ")
                    clean_question = question.split('.', 1)[-1].strip() if '.' in question else question
                    if clean_question:
                        # Create unique key for each button
                        button_key = f"next_step_{len(st.session_state.messages)}_{i}"
                        if st.button(clean_question, key=button_key):
                            st.session_state.follow_up_question = clean_question
                            st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Upload & Process")
    
    # File uploader widget
    uploaded_file = st.file_uploader(
        "Upload a CSV, PDF, DOCX, or TXT file",
        type=['csv', 'pdf', 'docx', 'txt'],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # Check if this file has already been processed
        if not st.session_state.ingestion_done:
            st.info("File detected. Click 'Process Document' to begin.")

            if st.button("Process Document"):
                # 1. Clear any previous database
                with st.spinner("Clearing old data..."):
                    clear_database()
                
                # 2. Save the file to a local directory
                file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # 3. Run the ingestion pipeline
                with st.spinner(f"Processing `{uploaded_file.name}`... This may take a moment."):
                    ingestion_pipe = IngestionPipeline()
                    ingestion_pipe.ingest_file(file_path)
                
                # 4. Update session state
                st.session_state.ingestion_done = True
                st.session_state.processed_filename = uploaded_file.name
                st.success("Document processed successfully!")
                # Force a rerun to update the main interface
                st.rerun()

    # Add a "New Chat" button to reset
    if st.session_state.ingestion_done:
        if st.button("Start New Chat / Upload New File"):
            st.session_state.ingestion_done = False
            st.session_state.messages = []
            st.session_state.processed_filename = None
            if "follow_up_question" in st.session_state:
                del st.session_state.follow_up_question
            clear_database()
            st.rerun()

    st.header("2. Configure")
    st.info("Configuration options will be available here in future updates.")

# --- MAIN CHAT INTERFACE ---
st.header("Ask Your Data")

if st.session_state.ingestion_done:
    st.info(f"Ready to answer questions about `{st.session_state.processed_filename}`")
    
    # Handle follow-up questions from button clicks
    if "follow_up_question" in st.session_state:
        follow_up = st.session_state.follow_up_question
        del st.session_state.follow_up_question
        handle_query(follow_up)
        st.rerun()
    
    # Summarize button
    if st.button("✨ Summarize Document"):
        user_summary_request = "Please summarize the document."
        st.session_state.messages.append({"role": "user", "content": user_summary_request})

        # Call the backend
        rag_pipe = st.session_state.rag_pipeline
        with st.chat_message("assistant"):
            with st.spinner("Generating summary..."):
                summary = rag_pipe.summarize_document(st.session_state.processed_filename)
                st.markdown(summary)
                # Add the summary to the message history
                st.session_state.messages.append({"role": "assistant", "content": summary})
        st.rerun()
    
    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input widget at the bottom
    if prompt := st.chat_input("Ask a question about your document..."):
        handle_query(prompt)
        st.rerun()

else:
    st.info("Please upload and process a document to get started.")