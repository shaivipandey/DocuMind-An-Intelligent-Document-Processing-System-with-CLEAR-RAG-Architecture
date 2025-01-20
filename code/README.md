# CLEAR-RAG: Advanced Document Intelligence System
### Developed by Shaivi Pandey | [GitHub](https://github.com/shaivipandey)

A sophisticated document management system powered by Entity-Augmented Retrieval Architecture (CLEAR-RAG) for intelligent processing, summarization, and semantic search across multiple document formats.

## Key Features

- Multi-Format Document Processing:
  - PDF document processing with advanced text extraction
  - HTML content processing with metadata preservation
  - Image processing with OCR capabilities
  
- CLEAR-RAG Architecture:
  - Entity-Based Processing for precise information retrieval
  - Hybrid Vector Search combining dense and sparse retrieval
  - Multi-Modal Analysis for comprehensive document understanding
  - Intelligent Context Retrieval with metadata enhancement
  
- Advanced AI Capabilities:
  - Document chunking with overlapping segments
  - Cross-attention based reranking using GPT-3.5
  - Zero-shot and few-shot learning capabilities
  - Automatic document summarization
  
- Interactive Interface:
  - Streamlit-based user interface
  - Real-time document processing
  - Interactive Q&A functionality
  - Document statistics and insights

## Technical Stack

- **Core Technologies:**
  - Python 3.8+
  - OpenAI API integration
  - Streamlit for frontend
  - PyPDF2 for PDF processing
  
- **AI/ML Components:**
  - OpenAI's GPT-3.5 for summarization
  - text-embedding-ada-002 for embeddings
  - BERT-based models for domain tasks
  - Custom NER implementation
  
- **Processing Pipeline:**
  - Document chunking system
  - Entity recognition module
  - Vector search implementation
  - Hybrid retrieval system

## Installation & Setup

1. **Environment Setup:**
   ```bash
   cd code
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuration:**
   ```bash
   cp .env.example .env
   # Edit .env and add required API keys:
   # OPENAI_API_KEY=your_api_key_here
   ```

3. **Additional Requirements:**
   - Tesseract OCR for image processing
   - NLTK data for text processing
   - Sufficient RAM for large document processing

## Usage

1. **Start the Application:**
   ```bash
   streamlit run app.py
   ```
   Access the interface at `http://localhost:8501`

2. **Document Processing:**
   - Upload documents (PDF/HTML/Images)
   - View real-time processing status
   - Access generated summaries
   - Interact with Q&A system

3. **Advanced Features:**
   - Entity-based search
   - Context-aware responses
   - Multi-format support
   - Processing statistics

## Project Architecture

### Core Components:
- `app.py`: Streamlit interface and main application logic
- `document_processor.py`: Multi-format document processing
- `document_chunker.py`: Advanced chunking with metadata
- `html_processor.py`: HTML content processing
- `image_processor.py`: Image processing with OCR
- `summarizer.py`: GPT-3.5 based summarization
- `vector_search.py`: Hybrid search implementation

### Directory Structure:
- `code/`: Source code and application logic
- `dataset/`: Document storage and management
- `output/`: Processed results and embeddings

## CLEAR-RAG Implementation

### Entity Processing:
- Named Entity Recognition (NER)
- Entity-based context retrieval
- Metadata preservation
- Positional tracking

### Search Architecture:
- Dense Retrieval: OpenAI embeddings
- Sparse Retrieval: BM25 algorithm
- Hybrid Scoring System
- Cross-Attention Reranking

### Performance Features:
- Efficient token usage
- Optimized processing time
- Smart chunking system
- Caching mechanisms

## Performance & Optimization

### Processing Efficiency:
- Optimized token usage
- Reduced API calls
- Smart caching system
- Memory management

### Error Handling:
- Comprehensive error detection
- Graceful failure recovery
- Input validation
- System state management

## Future Roadmap

### Planned Enhancements:
- Advanced authentication system
- Extended document format support
- Batch processing capabilities
- Enhanced visualization features
- API endpoint expansion
- Performance optimizations

### Research Directions:
- Advanced entity recognition
- Improved context understanding
- Enhanced multi-modal processing
- Real-time processing optimization

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for improvements and bug fixes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Special thanks to the open-source community and the developers of the various libraries and tools that made this project possible.
