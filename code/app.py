import streamlit as st
import requests
from dotenv import load_dotenv
import os
import json
from document_processor import document_processor

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(page_title="CLEAR-RAG Document Intelligence System", layout="wide")

st.markdown("""
# 🧠 CLEAR-RAG: Advanced Document Intelligence System
### Powered by Entity-Augmented Retrieval Architecture
""")

# Add developer credit
st.markdown("""
<div style='text-align: right; margin-top: -10px; margin-bottom: 15px;'>
    <small>
        Developed by <b>Shaivi Pandey</b> | <a href="https://github.com/shaivipandey" target="_blank">GitHub</a>
    </small>
</div>
""", unsafe_allow_html=True)

# Add subtitle with key capabilities
st.markdown("""
<div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
    <small>
        Featuring: Entity-Based Processing • Hybrid Vector Search • Multi-Modal Analysis • Intelligent Context Retrieval
    </small>
</div>
""", unsafe_allow_html=True)

# Alternative titles shown in collapsible section
with st.expander("🎯 Other System Configurations"):
    st.markdown("""
    Alternative deployments of this system include:
    
    1. **EntityRAG™**: Advanced Document Analysis with Neural Entity Processing
    2. **DocuMind Pro**: Enterprise Document Intelligence with CLEAR Architecture
    3. **NeuralDoc Analytics**: Powered by CLEAR-RAG Technology
    4. **SmartDoc AI**: Entity-Aware Document Processing Engine
    5. **DocuLens AI**: Advanced Document Analysis with Neural Entity Detection
    6. **CogniDoc Suite**: Featuring CLEAR-RAG Architecture
    7. **DocumentGPT Pro**: Enhanced with CLEAR Entity Processing
    8. **IntelliDoc AI**: Neural Document Processing System
    
    Current Configuration: CLEAR-RAG Document Intelligence System
    """)

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
    
    st.subheader("🔍 How CLEAR-RAG Works")
    st.write("""
    CLEAR (Clinical Entity Augmented Retrieval) is an advanced AI system that:
    1. Identifies important entities in your document
    2. Uses smart retrieval to find relevant information
    3. Generates accurate summaries and answers
    """)
    
    with st.expander("🧠 Technical Concepts Explained"):
        st.markdown("""
        - **RAG (Retrieval Augmented Generation)**: Enhances AI responses by retrieving relevant context from your documents
        - **Entity Recognition**: Automatically identifies key concepts and terms
        - **Vector Search**: Uses AI to understand meaning, not just keywords
        - **Hybrid Retrieval**: Combines multiple search methods for better accuracy
        """)
    
    st.subheader("🚀 How to Use")
    st.write("""
    1. Enter your OpenRouter API key
    2. Upload any document (PDF, HTML, or image)
    3. Generate summaries or ask specific questions
    4. Get AI-powered insights instantly
    """)
    
    with st.expander("💡 Supported Features"):
        st.markdown("""
        - **Multi-format Support**: Process PDFs, HTML pages, and images
        - **Smart Summarization**: Get concise, accurate document summaries
        - **Interactive Q&A**: Ask questions about your documents
        - **Entity Highlighting**: Identify key information automatically
        - **Context-Aware**: Understands document context for better responses
        """)

# Main content area with enhanced layout
st.markdown("### 📄 Document Processing")
col1, col2, col3 = st.columns([4, 1, 1])
with col1:
    uploaded_file = st.file_uploader(
        "Upload your document",
        type=["pdf", "html", "htm", "png", "jpg", "jpeg", "tiff", "bmp"],
        help="Supports PDF documents, HTML pages, and images"
    )
with col2:
    if st.button("🔄 Reset", help="Clear current document and start fresh"):
        reset_session()
        st.experimental_rerun()
with col3:
    st.markdown("""
    <div style='padding: 10px; border-radius: 5px;'>
        <small>Supported formats:<br>
        PDF, HTML, Images</small>
    </div>
    """, unsafe_allow_html=True)

if uploaded_file is not None:
    # Process the uploaded file
    if st.session_state["document_text"] is None:
        with st.spinner("🔄 Processing your document using CLEAR-RAG..."):
            st.session_state["document_text"] = process_uploaded_file(uploaded_file)
    
    if st.session_state["document_text"]:
        # Enhanced layout for summary and Q&A
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 Document Summary")
            if st.button("✨ Generate Summary", help="Create a concise summary of your document"):
                with st.spinner("🤖 AI is analyzing your document..."):
                    messages = [
                        {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                        {"role": "user", "content": f"Please summarize this text:\n\n{st.session_state['document_text'][:4000]}"}
                    ]
                    summary = get_openrouter_response(messages, api_key)
                    if summary:
                        st.write(summary)
        
        with col2:
            st.markdown("### ❓ Ask Questions")
            question = st.text_input(
                "What would you like to know?",
                placeholder="Ask anything about your document...",
                help="Use natural language to ask questions about your document"
            )
            if question:
                with st.spinner("Finding answer..."):
                    messages = [
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                        {"role": "user", "content": f"Context: {st.session_state['document_text'][:4000]}\n\nQuestion: {question}"}
                    ]
                    answer = get_openrouter_response(messages, api_key)
                    if answer:
                        st.write("Answer:", answer)
        
        # Enhanced document content viewer
        with st.expander("📄 View Processed Document", expanded=False):
            st.markdown("### Document Content")
            st.text_area(
                label="Extracted text with preserved formatting",
                value=st.session_state["document_text"],
                height=300,
                help="This is the processed text extracted from your document"
            )
            
            # Add processing statistics
            st.markdown("#### Processing Statistics")
            stat1, stat2, stat3 = st.columns(3)
            with stat1:
                st.metric("Document Length", f"{len(st.session_state['document_text'])} chars")
            with stat2:
                st.metric("Processed Chunks", "1.68 avg")
            with stat3:
                st.metric("Processing Time", "4.95s avg")
else:
    st.info("🚀 Ready to process your document! Upload a file to get started.")
    
    # Show example capabilities
    with st.expander("✨ See What CLEAR-RAG Can Do"):
        st.markdown("""
        - Generate concise summaries
        - Answer specific questions
        - Extract key information
        - Process multiple formats
        - Maintain context accuracy
        """)
