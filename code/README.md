# AI-Powered Document Management System

A simple yet powerful document management system that uses AI to process, summarize, and enable semantic search across PDF documents.

## Features

- PDF document upload and text extraction
- Advanced RAG (Retrieval Augmented Generation) implementation:
  - Document chunking with overlapping segments for better context preservation
  - Hybrid search combining dense (embeddings) and sparse (BM25) retrieval
  - Cross-attention based reranking using GPT-3.5
  - Metadata-enhanced document chunks for improved context
- Automatic document summarization using GPT-3.5
- RESTful API interface

## Prerequisites

- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

## Setup

1. Clone the repository and navigate to the project directory:

```bash
cd code
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Upload Document
```http
POST /upload/
```
Upload a PDF document for processing. The system will:
- Extract text from the PDF
- Generate a summary using GPT-3.5
- Create document embeddings for search

### List Documents
```http
GET /documents/
```
Get a list of all processed documents and their metadata.

### Search Documents
```http
GET /search/?query=your_search_query&top_k=5
```
Search through documents using semantic similarity. Parameters:
- `query`: Your search query
- `top_k`: Number of results to return (default: 5)

## Project Structure

- `app.py`: Main FastAPI application and API endpoints
- `document_processor.py`: PDF text extraction functionality
- `document_chunker.py`: Advanced document chunking with metadata
- `summarizer.py`: Document summarization using OpenAI's GPT-3.5
- `vector_search.py`: Hybrid search implementation (dense + sparse) with reranking
- `requirements.txt`: Project dependencies
- `.env`: Configuration for API keys (not in version control)

## RAG Implementation Details

### Document Chunking
- Implements overlapping chunks to preserve context across segment boundaries
- Maintains document metadata and positional information
- Configurable chunk size and overlap parameters

### Hybrid Search
- Dense Retrieval: Uses OpenAI embeddings for semantic similarity
- Sparse Retrieval: Implements BM25 algorithm for keyword matching
- Score Combination: Weighted combination of dense and sparse scores
- Cross-Attention Reranking: Uses GPT-3.5 to rerank results based on relevance

### Vector Search
- Embedding Model: OpenAI's text-embedding-ada-002
- Similarity Metric: Cosine similarity
- Caching: Persistent storage of embeddings for efficiency

## Example Usage

1. Start the server
2. Upload a PDF document:
```bash
curl -X POST -F "file=@your_document.pdf" http://localhost:8000/upload/
```

3. Search documents:
```bash
curl "http://localhost:8000/search/?query=your search query"
```

## Directory Structure

The system uses two main directories:
- `dataset/`: Stores uploaded PDF files
- `output/`: Stores processed text, metadata, and embeddings

## Error Handling

The API includes comprehensive error handling for:
- Invalid file types
- Processing errors
- API failures
- File system errors

## Future Improvements

Potential enhancements:
- Support for more document types (Word, Images with OCR)
- User authentication
- Document versioning
- Web interface
- Batch processing
- Export functionality
