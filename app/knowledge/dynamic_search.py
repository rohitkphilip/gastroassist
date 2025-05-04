from typing import Dict, Any, List
from app.knowledge.search_engines.tavily_search import TavilySearch
from app.knowledge.search_engines.duckduckgo_search import DuckDuckGoSearch

class DynamicSearch:
    """
    Performs dynamic searches across medical and general search engines
    """
    
    def __init__(self):
        """Initialize the dynamic search component"""
        self.tavily_search = TavilySearch()
        self.duckduckgo_search = DuckDuckGoSearch()
    
    def search(self, query: str, search_type: str = "combined") -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform a dynamic search for the given query
        
        Args:
            query: The search query
            search_type: Type of search to perform (medical, general, or combined)
            
        Returns:
            Dictionary containing search results from different sources
        """
        results = {}
        
        if search_type in ["medical", "combined"]:
            results["medical"] = self._search_medical(query)
            
        if search_type in ["general", "combined"]:
            results["general"] = self._search_general(query)
            
        return results
    
    def _search_medical(self, query: str) -> List[Dict[str, Any]]:
        """Perform a search using medical search engines"""
        # Use Tavily with medical filter for medical searches
        medical_results = self.tavily_search.search(
            query=query,
            search_depth="comprehensive",
            filter_medical=True
        )
        
        # Add source information to each result
        for result in medical_results:
            result["source"] = "tavily_medical"
        
        return medical_results
    
    def _search_general(self, query: str) -> List[Dict[str, Any]]:
        """Perform a search using general search engines"""
        # Use DuckDuckGo for general searches
        general_results = self.duckduckgo_search.search(
            query=query,
            max_results=10
        )
        
        # Add source information to each result if not already present
        for result in general_results:
            if "source" not in result:
                result["source"] = "duckduckgo"
        
        return general_results

