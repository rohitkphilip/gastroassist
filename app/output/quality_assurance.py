from typing import Dict, Any, List
import os
from dotenv import load_dotenv

class QualityAssurance:
    """
    Performs quality checks on generated answers
    """
    
    def __init__(self):
        """Initialize the quality assurance component"""
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize any required resources
        pass
    
    def check(self, answer: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check the quality of a generated answer
        
        Args:
            answer: The generated answer
            sources: The source information
            
        Returns:
            Quality assessment results
        """
        # Simple quality checks for now
        word_count = len(answer.split())
        source_count = len(sources)
        
        # Calculate a simple confidence score
        confidence_score = 0.0
        if source_count > 0:
            # Average the confidence of the sources
            source_confidences = [s.get("confidence", 0.0) for s in sources]
            avg_source_confidence = sum(source_confidences) / len(source_confidences)
            
            # Factor in the number of sources and word count
            source_factor = min(source_count / 5, 1.0)  # Cap at 1.0
            length_factor = min(word_count / 100, 1.0)  # Cap at 1.0
            
            confidence_score = avg_source_confidence * 0.6 + source_factor * 0.2 + length_factor * 0.2
        
        return {
            "confidence_score": confidence_score,
            "word_count": word_count,
            "source_count": source_count,
            "has_medical_sources": any(s.get("type") == "medical" for s in sources)
        }
    
    def verify(self, answer: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Alias for check() method to maintain backward compatibility
        
        Args:
            answer: The generated answer
            sources: The source information
        
        Returns:
            Quality assessment results
        """
        return self.check(answer, sources)

