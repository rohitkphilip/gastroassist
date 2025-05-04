from typing import Dict, Any, List
import os
from dotenv import load_dotenv

class ReasoningAgent:
    """
    Analyzes queries and determines information needs
    """
    
    def __init__(self):
        """Initialize the reasoning agent"""
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize any required resources
        pass
    
    def analyze(self, processed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze a processed query to determine information needs
        
        Args:
            processed_query: The processed query information
            
        Returns:
            List of information needs
        """
        # Simple analysis for now
        query_text = processed_query["normalized_text"]
        
        # Extract potential information needs
        information_needs = [
            {
                "type": "general",
                "query": query_text,
                "priority": 1.0
            }
        ]
        
        # Add medical-specific query if it seems health-related
        medical_terms = ["symptom", "disease", "treatment", "medication", 
                         "doctor", "pain", "stomach", "digest", "acid", 
                         "reflux", "gerd", "ibs", "crohn", "colitis", "ulcer"]
        
        if any(term in query_text for term in medical_terms):
            information_needs.append({
                "type": "medical",
                "query": f"medical {query_text}",
                "priority": 1.5
            })
        
        return information_needs
