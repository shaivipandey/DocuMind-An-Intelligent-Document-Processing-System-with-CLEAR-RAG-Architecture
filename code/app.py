import streamlit as st
import requests
from dotenv import load_dotenv
import os
import json
from document_processor import document_processor

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(page_title="Document Q&A Assistant", layout="wide")
st.title("📄 Document Q&A Assistant")

# Initialize session state
if "document_text" not in st.session_state:
    st.session_state["document_text"] = None

# Reset function
def reset_session():
    st.session_state["document_text"] = None

def process_uploaded_file(uploaded_file):
    """Process uploaded file (PDF or HTML)"""
    temp_path = None
    try:
        # Save the uploaded file temporarily with proper encoding
        file_type = uploaded_file.name.lower().split('.')[-1]
        # Create temporary file in the output directory with absolute path
        temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        
        print(f"Processing file: {uploaded_file.name} (type: {file_type})")  # Debug log
        print(f"Using temporary path: {temp_path}")  # Debug log
        
        try:
            if file_type in ['html', 'htm']:
                # For HTML files, decode and save with UTF-8 encoding
                content = uploaded_file.getvalue().decode('utf-8')
                with open(temp_path, "w", encoding='utf-8') as f:
                    f.write(content)
                print(f"Saved HTML content to {temp_path}")  # Debug log
            else:
                # For PDFs and other binary files
                content = uploaded_file.getvalue()
                print(f"Read {len(content)} bytes from uploaded PDF")  # Debug log
                with open(temp_path, "wb") as f:
                    f.write(content)
                print(f"Saved PDF content to {temp_path}")  # Debug log
                # Verify the file was written correctly
                if not os.path.exists(temp_path):
                    raise Exception("Failed to save temporary file")
                saved_size = os.path.getsize(temp_path)
                print(f"Verified saved file size: {saved_size} bytes")  # Debug log
                if saved_size == 0:
                    raise Exception("Saved file is empty")
        except UnicodeDecodeError:
            st.error("Error: The HTML file must be UTF-8 encoded")
            return None
        except Exception as e:
            st.error(f"Error saving file: {str(e)}")
            return None
        
        st.info(f"Processing {uploaded_file.name}...")
        
        try:
            # Process the file using document processor
            print(f"Calling document processor for {temp_path}")  # Debug log
            result = document_processor.process_document(temp_path)
            if not result:
                raise Exception("Document processing failed - no result returned")
            
            print(f"Document processing result: {result}")  # Debug log
            
            # Get the extracted text
            print(f"Getting text for filename: {result.get('filename', 'NO_FILENAME')}")  # Debug log
            extracted_text = document_processor.get_document_text(result["filename"])
            if not extracted_text:
                raise Exception("No text could be extracted from the document")
            
            print(f"Successfully extracted {len(extracted_text)} characters")  # Debug log
            return extracted_text
            
        except Exception as e:
            st.error(f"Error during document processing: {str(e)}")
            # Log additional debug information
            print(f"File type: {file_type}")
            print(f"Temp path: {temp_path}")
            print(f"Error details: {str(e)}")
            return None
        
    except Exception as e:
        st.error(f"Error processing file {uploaded_file.name}: {str(e)}")
        return None
        
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                st.warning(f"Could not remove temporary file: {str(e)}")

def get_openrouter_response(messages, api_key):
    """Get response using OpenRouter API"""
    if not api_key:
        st.error("Please enter your OpenRouter API key in the sidebar.")
        return None
        
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:8501",  # Required for OpenRouter
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mistralai/mistral-7b-instruct",  # Free tier model
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            st.error(f"API Error: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error calling OpenRouter API: {str(e)}")
        return None

# Sidebar configuration
with st.sidebar:
    st.subheader("Configuration")
    api_key = st.text_input(
        "OpenRouter API Key",
        value=os.getenv("OPENROUTER_API_KEY", ""),
        type="password",
        key="openrouter_api_key"
    )
    if api_key:
        st.success("API key configured!")
    
    st.subheader("How to Use")
    st.write("""
    1. Enter your OpenRouter API key
    2. Upload a PDF, HTML, or image document
    3. Click 'Generate Summary' or ask questions
    """)
    
    st.subheader("Features")
    st.write("""
    - PDF, HTML, and image document processing
    - AI-powered summarization
    - Question answering
    - Easy-to-use interface
    """)

# Main content
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("1. Upload Your Document")
    uploaded_file = st.file_uploader("Choose a PDF, HTML, or image file", type=["pdf", "html", "htm", "png", "jpg", "jpeg", "tiff", "bmp"])
with col2:
    st.subheader("Reset")
    if st.button("Clear Document"):
        reset_session()
        st.experimental_rerun()

if uploaded_file is not None:
    # Process the uploaded file
    if st.session_state["document_text"] is None:
        with st.spinner("Processing document..."):
            st.session_state["document_text"] = process_uploaded_file(uploaded_file)
    
    if st.session_state["document_text"]:
        # Create two columns for summary and Q&A
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("2. Document Summary")
            if st.button("Generate Summary"):
                with st.spinner("Generating summary..."):
                    messages = [
                        {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                        {"role": "user", "content": f"Please summarize this text:\n\n{st.session_state['document_text'][:4000]}"}
                    ]
                    summary = get_openrouter_response(messages, api_key)
                    if summary:
                        st.write(summary)
        
        with col2:
            st.subheader("3. Ask Questions")
            question = st.text_input("What would you like to know about the document?")
            if question:
                with st.spinner("Finding answer..."):
                    messages = [
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                        {"role": "user", "content": f"Context: {st.session_state['document_text'][:4000]}\n\nQuestion: {question}"}
                    ]
                    answer = get_openrouter_response(messages, api_key)
                    if answer:
                        st.write("Answer:", answer)
        
        # Show extracted text (collapsible)
        with st.expander("View Extracted Text"):
            st.text_area(
                label="Document Content",
                value=st.session_state["document_text"],
                height=300
            )
else:
    st.info("👆 Upload a PDF, HTML, or image file to get started!")
