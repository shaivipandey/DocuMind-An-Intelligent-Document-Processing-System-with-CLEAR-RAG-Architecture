from typing import List, Dict, Any
import numpy as np
from nltk.tokenize import sent_tokenize
import nltk
import json
import os

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class DocumentChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.output_dir = "../output/chunks"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_chunks(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create overlapping chunks from document text with metadata.
        """
        # Split text into sentences
        sentences = sent_tokenize(text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            if current_size + sentence_size > self.chunk_size and current_chunk:
                # Store current chunk
                chunk_text = " ".join(current_chunk)
                chunk_data = {
                    "text": chunk_text,
                    "metadata": {
                        **metadata,
                        "chunk_id": len(chunks),
                        "start_idx": max(0, len(chunks) * (self.chunk_size - self.chunk_overlap)),
                        "length": len(chunk_text)
                    }
                }
                chunks.append(chunk_data)
                
                # Keep overlapping sentences for next chunk
                overlap_size = 0
                overlap_chunk = []
                
                for s in reversed(current_chunk):
                    if overlap_size + len(s) <= self.chunk_overlap:
                        overlap_chunk.insert(0, s)
                        overlap_size += len(s)
                    else:
                        break
                
                current_chunk = overlap_chunk
                current_size = overlap_size
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Add final chunk if it exists
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_data = {
                "text": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk_id": len(chunks),
                    "start_idx": max(0, len(chunks) * (self.chunk_size - self.chunk_overlap)),
                    "length": len(chunk_text)
                }
            }
            chunks.append(chunk_data)
        
        return chunks
    
    def save_chunks(self, filename: str, chunks: List[Dict[str, Any]]):
        """
        Save document chunks to disk.
        """
        chunks_file = os.path.join(self.output_dir, f"{filename}_chunks.json")
        with open(chunks_file, "w") as f:
            json.dump(chunks, f, indent=2)
        return chunks_file
    
    def load_chunks(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load document chunks from disk.
        """
        chunks_file = os.path.join(self.output_dir, f"{filename}_chunks.json")
        if not os.path.exists(chunks_file):
            raise FileNotFoundError(f"Chunks file not found: {chunks_file}")
            
        with open(chunks_file, "r") as f:
            return json.load(f)

# Create a global instance
document_chunker = DocumentChunker()
