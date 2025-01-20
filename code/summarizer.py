import os
import openai
from typing import Dict, Any
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_summary(text: str, max_length: int = 1000) -> str:
    """
    Generate a summary of the text using OpenAI's GPT model.
    """
    try:
        # Truncate text if it's too long
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise summaries of documents."},
                {"role": "user", "content": f"Please provide a concise summary of the following text:\n\n{text}"}
            ],
            max_tokens=150,
            temperature=0.5
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        raise Exception(f"Error generating summary: {str(e)}")

def process_and_summarize(filename: str) -> Dict[str, Any]:
    """
    Process a document and generate its summary.
    """
    try:
        output_dir = "../output"
        
        # Read the document text
        text_file_path = os.path.join(output_dir, f"{filename}.txt")
        if not os.path.exists(text_file_path):
            raise Exception("Document text not found")
        
        with open(text_file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        # Generate summary
        summary = generate_summary(text)
        
        # Update document info
        info_file_path = os.path.join(output_dir, f"{filename}.json")
        with open(info_file_path, "r") as f:
            doc_info = json.load(f)
        
        doc_info["summary"] = summary
        doc_info["status"] = "summarized"
        
        # Save updated info
        with open(info_file_path, "w") as f:
            json.dump(doc_info, f, indent=2)
        
        return doc_info
    
    except Exception as e:
        raise Exception(f"Error processing and summarizing document: {str(e)}")
