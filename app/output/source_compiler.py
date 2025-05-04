from typing import Dict, Any, List
import os
from dotenv import load_dotenv

class SourceCompiler:
    """
    Compiles and formats source information
    """
    
    def __init__(self):
        """Initialize the source compiler"""
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize any required resources
        pass
    
    def compile(self, knowledge_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Compile source information from knowledge results
        
        Args:
            knowledge_results: The retrieved knowledge
            
        Returns:
            List of formatted source information
        """
        sources = []
        
        # Process medical sources
        if "medical" in knowledge_results:
            for result in knowledge_results["medical"]:
                source = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", ""),
                    "confidence": result.get("score", 0.0),
                    "type": "medical"
                }
                sources.append(source)
        
        # Process general sources
        if "general" in knowledge_results:
            for result in knowledge_results["general"]:
                source = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", ""),
                    "confidence": result.get("score", 0.0) if "score" in result else 0.7,
                    "type": "general"
                }
                sources.append(source)
        
        # Sort sources by confidence
        sources.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
        
        return sources
