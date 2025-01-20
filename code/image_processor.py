from PIL import Image
import pytesseract
from datetime import datetime
import os
from typing import Dict, Any
import json
import logging

class ImageProcessor:
    """
    Process image files with OCR capabilities and metadata extraction.
    Follows the project's processor pattern like document_processor and html_processor.
    """
    def __init__(self):
        # Match the project's output directory pattern
        self.output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Image processor initialized with output directory: {self.output_dir}")  # Match debug log pattern
        
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Pre-process image to improve OCR accuracy.
        """
        try:
            # Convert to grayscale
            image = image.convert('L')
            
            # Increase contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            return image
        except Exception as e:
            raise Exception(f"Error preprocessing image: {str(e)}")

    def extract_metadata(self, image_path: str) -> Dict[str, Any]:
        """
        Extract metadata from image file.
        """
        try:
            with Image.open(image_path) as img:
                metadata = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "creation_time": datetime.fromtimestamp(
                        os.path.getctime(image_path)
                    ).isoformat(),
                    "modification_time": datetime.fromtimestamp(
                        os.path.getmtime(image_path)
                    ).isoformat(),
                    "file_size": os.path.getsize(image_path)
                }
                
                # Extract EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    if exif:
                        metadata['exif'] = {
                            str(k): str(v) for k, v in exif.items()
                        }
                
                return metadata
        except Exception as e:
            raise Exception(f"Error extracting metadata: {str(e)}")

    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image using OCR.
        """
        try:
            with Image.open(image_path) as img:
                # Preprocess image
                processed_img = self.preprocess_image(img)
                
                # Perform OCR
                text = pytesseract.image_to_string(processed_img)
                return text.strip()
        except Exception as e:
            raise Exception(f"Error performing OCR: {str(e)}")

    def process(self, image_path: str) -> Dict[str, Any]:
        """
        Process image file: extract text and metadata.
        Follows similar pattern to html_processor.process().
        """
        try:
            # Extract text and metadata
            extracted_text = self.extract_text(image_path)
            metadata = self.extract_metadata(image_path)
            
            # Create document info
            filename = os.path.basename(image_path)
            doc_info = {
                "filename": filename,
                "file_type": "image",
                "metadata": metadata,
                "text_length": len(extracted_text),
                "status": "processed"
            }
            
            # Save extracted text (following project pattern)
            text_file_path = os.path.join(self.output_dir, f"{filename}.txt")
            print(f"Saving text to: {text_file_path}")  # Debug log
            with open(text_file_path, "w", encoding="utf-8") as f:
                f.write(extracted_text)
            
            # Save document info (following project pattern)
            info_file_path = os.path.join(self.output_dir, f"{filename}.json")
            print(f"Saving info to: {info_file_path}")  # Debug log
            with open(info_file_path, "w", encoding="utf-8") as f:
                json.dump(doc_info, f, indent=2)
            
            return doc_info
            
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

    def get_processed_text(self, filename: str) -> str:
        """
        Retrieve processed text for a document.
        Matches pattern from html_processor.
        """
        try:
            text_file_path = os.path.join(self.output_dir, f"{filename}.txt")
            
            if not os.path.exists(text_file_path):
                raise Exception("Processed text not found")
            
            with open(text_file_path, "r", encoding="utf-8") as f:
                return f.read()
                
        except Exception as e:
            raise Exception(f"Error retrieving processed text: {str(e)}")

# Create a global instance (following project pattern)
image_processor = ImageProcessor()
