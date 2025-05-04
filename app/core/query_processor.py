from typing import Dict, Any
import os
from dotenv import load_dotenv

class QueryProcessor:
    """
    Processes and analyzes user queries to extract key information
    """
    
    def __init__(self):
        """Initialize the query processor"""
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize any required resources
        pass
    
    def process(self, query_text: str) -> Dict[str, Any]:
        """
        Process a user query to extract key information
        
        Args:
            query_text: The raw query text from the user
            
        Returns:
            Dictionary containing processed query information
        """
        # Basic processing for now
        processed_query = {
            "original_text": query_text,
            "normalized_text": query_text.lower().strip(),
            "word_count": len(query_text.split()),
            "is_question": query_text.strip().endswith("?")
        }
        
        return processed_query
