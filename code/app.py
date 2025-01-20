import streamlit as st
import PyPDF2
import requests
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(page_title="PDF Q&A Assistant", layout="wide")
st.title("📄 PDF Q&A Assistant")

# Initialize session state
if "pdf_text" not in st.session_state:
    st.session_state["pdf_text"] = None

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

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
    2. Upload a PDF document
    3. Click 'Generate Summary' or ask questions
    """)
    
    st.subheader("Features")
    st.write("""
    - PDF text extraction
    - AI-powered summarization
    - Question answering
    - Easy-to-use interface
    """)

# Main content
st.subheader("1. Upload Your PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Extract text from PDF
    if st.session_state["pdf_text"] is None:
        with st.spinner("Extracting text from PDF..."):
            st.session_state["pdf_text"] = extract_text_from_pdf(uploaded_file)
    
    if st.session_state["pdf_text"]:
        # Create two columns for summary and Q&A
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("2. Document Summary")
            if st.button("Generate Summary"):
                with st.spinner("Generating summary..."):
                    messages = [
                        {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                        {"role": "user", "content": f"Please summarize this text:\n\n{st.session_state['pdf_text'][:4000]}"}
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
                        {"role": "user", "content": f"Context: {st.session_state['pdf_text'][:4000]}\n\nQuestion: {question}"}
                    ]
                    answer = get_openrouter_response(messages, api_key)
                    if answer:
                        st.write("Answer:", answer)
        
        # Show extracted text (collapsible)
        with st.expander("View Extracted Text"):
            st.text_area(
                label="Document Content",
                value=st.session_state["pdf_text"],
                height=300
            )
else:
    st.info("👆 Upload a PDF file to get started!")
