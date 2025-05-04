from typing import Dict, Any, List
import os
from dotenv import load_dotenv

class AnswerGenerator:
    """
    Generates answers based on retrieved knowledge
    """
    
    def __init__(self):
        """Initialize the answer generator"""
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize any required resources
        pass
    
    def generate(self, knowledge_results: Dict[str, Any], query: str) -> str:
        """
        Generate an answer based on retrieved knowledge
        
        Args:
            knowledge_results: The retrieved knowledge
            query: The original query
            
        Returns:
            Generated answer text
        """
        # Simple answer generation for now
        answer_parts = ["Based on the information I found:"]
        
        # Add medical information if available
        if "medical" in knowledge_results and knowledge_results["medical"]:
            medical_results = knowledge_results["medical"][:2]  # Use top 2 results
            for result in medical_results:
                answer_parts.append(f"- {result.get('snippet', '')}")
        
        # Add general information if available
        if "general" in knowledge_results and knowledge_results["general"]:
            general_results = knowledge_results["general"][:2]  # Use top 2 results
            for result in general_results:
                answer_parts.append(f"- {result.get('snippet', '')}")
        
        # If no results were found
        if len(answer_parts) == 1:
            answer_parts.append("I couldn't find specific information about your query. "
                               "Please try rephrasing or ask a different question.")
        
        return "\n\n".join(answer_parts)
