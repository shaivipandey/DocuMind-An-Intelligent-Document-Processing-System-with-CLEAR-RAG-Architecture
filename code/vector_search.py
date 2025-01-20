import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple
import openai
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from document_chunker import document_chunker
import nltk
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/words')
except LookupError:
    nltk.download('punkt')

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

class VectorSearch:
    def __init__(self):
        self.output_dir = "../output"
        self.embeddings_dir = os.path.join(self.output_dir, "embeddings")
        os.makedirs(self.embeddings_dir, exist_ok=True)
        self.bm25 = None
        self.documents = []
        self.initialize_bm25()
    
    def initialize_bm25(self):
        """
        Initialize BM25 index for hybrid search.
        """
        try:
            # Load all document chunks
            chunks = []
            chunk_texts = []
            for filename in os.listdir(document_chunker.output_dir):
                if filename.endswith('_chunks.json'):
                    with open(os.path.join(document_chunker.output_dir, filename)) as f:
                        doc_chunks = json.load(f)
                        chunks.extend(doc_chunks)
                        chunk_texts.extend([chunk["text"] for chunk in doc_chunks])
            
            # Tokenize texts for BM25
            tokenized_texts = [word_tokenize(text.lower()) for text in chunk_texts]
            self.bm25 = BM25Okapi(tokenized_texts)
            self.documents = chunks
        except Exception as e:
            print(f"Warning: Could not initialize BM25 index: {str(e)}")
    
    def compute_embedding(self, text: str) -> List[float]:
        """
        Compute embeddings for the given text using OpenAI's API.
        """
        try:
            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error computing embedding: {str(e)}")
    
    def save_embedding(self, filename: str, embedding: List[float]):
        """
        Save embedding to a file.
        """
        embedding_path = os.path.join(self.embeddings_dir, f"{filename}.json")
        with open(embedding_path, "w") as f:
            json.dump({
                "filename": filename,
                "embedding": embedding
            }, f)
    
    def load_embeddings(self) -> Dict[str, List[float]]:
        """
        Load all saved embeddings.
        """
        embeddings = {}
        for filename in os.listdir(self.embeddings_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.embeddings_dir, filename)) as f:
                    data = json.load(f)
                    embeddings[data["filename"]] = data["embedding"]
        return embeddings
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def hybrid_search(self, query: str, top_k: int = 5, alpha: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining dense and sparse retrievals with reranking.
        """
        try:
            # Dense retrieval (vector similarity)
            query_embedding = self.compute_embedding(query)
            dense_scores = []
            
            for doc in self.documents:
                doc_embedding = self.compute_embedding(doc["text"])
                similarity = self.compute_similarity(query_embedding, doc_embedding)
                dense_scores.append(similarity)
            
            # Sparse retrieval (BM25)
            if self.bm25:
                tokenized_query = word_tokenize(query.lower())
                sparse_scores = self.bm25.get_scores(tokenized_query)
                
                # Normalize scores
                sparse_scores = np.array(sparse_scores) / max(sparse_scores) if max(sparse_scores) > 0 else sparse_scores
                dense_scores = np.array(dense_scores) / max(dense_scores) if max(dense_scores) > 0 else dense_scores
                
                # Combine scores
                combined_scores = alpha * dense_scores + (1 - alpha) * sparse_scores
            else:
                combined_scores = dense_scores
            
            # Get top k results
            top_indices = np.argsort(combined_scores)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                doc = self.documents[idx]
                results.append({
                    "text": doc["text"],
                    "metadata": doc["metadata"],
                    "score": float(combined_scores[idx])
                })
            
            # Rerank results using cross-attention
            reranked_results = self.rerank_results(query, results)
            return reranked_results
        
        except Exception as e:
            raise Exception(f"Error searching documents: {str(e)}")

    def rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rerank results using GPT model for better relevance.
        """
        try:
            reranked = []
            for result in results:
                # Use GPT to evaluate relevance
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a document relevance expert. Rate the relevance of the passage to the query on a scale of 0-1."},
                        {"role": "user", "content": f"Query: {query}\n\nPassage: {result['text']}\n\nProvide only the numerical score (0-1):"}
                    ],
                    max_tokens=10,
                    temperature=0.1
                )
                
                try:
                    relevance_score = float(response.choices[0].message.content.strip())
                    result["relevance_score"] = relevance_score
                    reranked.append(result)
                except ValueError:
                    result["relevance_score"] = 0.0
                    reranked.append(result)
            
            # Sort by relevance score
            reranked.sort(key=lambda x: x["relevance_score"], reverse=True)
            return reranked
        except Exception as e:
            print(f"Warning: Reranking failed: {str(e)}")
            return results

# Create a global instance
vector_search = VectorSearch()
