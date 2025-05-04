from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from app.knowledge.dynamic_search import DynamicSearch

class KnowledgeRouter:
    """
    Routes information needs to appropriate knowledge sources
    """
    
    def __init__(self):
        """Initialize the knowledge router"""
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize search components
        self.dynamic_search = DynamicSearch()
    
    def retrieve(self, information_needs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Retrieve information based on the identified needs
        
        Args:
            information_needs: List of information needs
            
        Returns:
            Dictionary containing retrieved knowledge
        """
        results = {}
        
        # Process each information need
        for need in information_needs:
            need_type = need.get("type", "general")
            query = need.get("query", "")
            
            if need_type == "medical":
                # Use medical-specific search
                search_results = self.dynamic_search.search(query, search_type="medical")
                results["medical"] = search_results.get("medical", [])
            elif need_type == "general":
                # Use general search
                search_results = self.dynamic_search.search(query, search_type="general")
                results["general"] = search_results.get("general", [])
        
        return results


