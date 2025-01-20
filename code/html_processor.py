from bs4 import BeautifulSoup
import requests
from typing import Dict, Any, Union
import os
import json
from urllib.parse import urlparse

class HTMLProcessor:
    """
    Process HTML content from files or URLs, extracting clean text and metadata.
    """
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"HTML Processor initialized with output directory: {self.output_dir}")  # Debug log

    def is_url(self, path: str) -> bool:
        """Check if the given path is a URL."""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def get_html_content(self, path: str) -> str:
        """
        Get HTML content from either a local file or URL.
        """
        try:
            if self.is_url(path):
                response = requests.get(path, timeout=10)
                response.raise_for_status()
                return response.text
            else:
                with open(path, 'r', encoding='utf-8') as file:
                    return file.read()
        except Exception as e:
            raise Exception(f"Error reading HTML content: {str(e)}")

    def extract_text_and_metadata(self, html_content: str) -> Dict[str, Any]:
        """
        Extract clean text and metadata from HTML content.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style']):
                element.decompose()
            
            # Extract metadata
            metadata = {
                "title": soup.title.string if soup.title else None,
                "meta_description": None,
                "meta_keywords": None,
                "headings": {
                    "h1": [h.get_text(strip=True) for h in soup.find_all('h1')],
                    "h2": [h.get_text(strip=True) for h in soup.find_all('h2')],
                    "h3": [h.get_text(strip=True) for h in soup.find_all('h3')]
                }
            }
            
            # Get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                metadata['meta_description'] = meta_desc.get('content')
            
            # Get meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                metadata['meta_keywords'] = meta_keywords.get('content')
            
            # Extract main content
            # Get text from p, li, div, and other content tags
            content_tags = soup.find_all(['p', 'li', 'div', 'article', 'section'])
            text_content = '\n'.join(tag.get_text(strip=True) for tag in content_tags if tag.get_text(strip=True))
            
            return {
                "text": text_content,
                "metadata": metadata
            }
        except Exception as e:
            raise Exception(f"Error extracting content from HTML: {str(e)}")

    def process(self, path: str) -> Dict[str, Any]:
        """
        Process HTML content and save extracted information.
        """
        try:
            # Get HTML content
            html_content = self.get_html_content(path)
            
            # Extract text and metadata
            extracted_data = self.extract_text_and_metadata(html_content)
            
            # Create document info with sanitized filename
            if self.is_url(path):
                filename = urlparse(path).netloc
            else:
                # Keep the original filename but ensure it's properly sanitized
                filename = os.path.basename(path)
                # Don't modify the filename as document_processor expects the original name
            doc_info = {
                "source": path,
                "is_url": self.is_url(path),
                "metadata": extracted_data["metadata"],
                "text_length": len(extracted_data["text"]),
                "status": "processed"
            }
            
            # Save extracted text
            text_file_path = os.path.join(self.output_dir, f"{filename}.txt")
            print(f"Saving text to: {text_file_path}")  # Debug log
            with open(text_file_path, "w", encoding="utf-8") as f:
                f.write(extracted_data["text"])
            
            # Save document info
            info_file_path = os.path.join(self.output_dir, f"{filename}.json")
            print(f"Saving info to: {info_file_path}")  # Debug log
            with open(info_file_path, "w", encoding="utf-8") as f:
                json.dump(doc_info, f, indent=2)
            
            return doc_info
        
        except Exception as e:
            raise Exception(f"Error processing HTML document: {str(e)}")

    def get_processed_text(self, filename: str) -> str:
        """
        Retrieve processed text for a document.
        """
        try:
            text_file_path = os.path.join(self.output_dir, f"{filename}.txt")
            
            if not os.path.exists(text_file_path):
                raise Exception("Processed text not found")
            
            with open(text_file_path, "r", encoding="utf-8") as f:
                return f.read()
        
        except Exception as e:
            raise Exception(f"Error retrieving processed text: {str(e)}")

# Create a global instance
html_processor = HTMLProcessor()
