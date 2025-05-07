from typing import Dict, Any, List
from app.knowledge.search_engines.tavily_search import TavilySearch
from app.knowledge.search_engines.tavily_extract import TavilyExtract
from app.knowledge.search_engines.duckduckgo_search import DuckDuckGoSearch

class DynamicSearch:
    """
    Performs dynamic searches across medical and general search engines
    with content extraction capabilities
    """
    
    def __init__(self):
        """Initialize the dynamic search component"""
        self.tavily_search = TavilySearch()
        self.duckduckgo_search = DuckDuckGoSearch()
        self.tavily_extract = TavilyExtract()
    
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
    
    def extract_content(self, url: str, extractor: str = "tavily") -> Dict[str, Any]:
        """
        Extract detailed content from a URL
        
        Args:
            url: The URL to extract content from
            extractor: The extraction service to use
            
        Returns:
            Dictionary containing the extracted content
        """
        if extractor == "tavily":
            return self.tavily_extract.extract(url)
        else:
            raise ValueError(f"Unsupported extractor: {extractor}")
    
    def search_and_extract(self, query: str, search_type: str = "medical", max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Combined search and extraction in a single operation
        
        Args:
            query: The search query
            search_type: Type of search to perform (medical, general, or combined)
            max_results: Maximum number of results to extract content from
            
        Returns:
            List of results with extracted content
        """
        # First perform the search
        search_results = self.search(query, search_type)
        
        # Flatten the results based on search type
        flat_results = []
        if search_type == "medical" and "medical" in search_results:
            flat_results = search_results["medical"]
        elif search_type == "general" and "general" in search_results:
            flat_results = search_results["general"]
        elif search_type == "combined":
            if "medical" in search_results:
                flat_results.extend(search_results["medical"])
            if "general" in search_results:
                flat_results.extend(search_results["general"])
        
        # Sort by score if available
        flat_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Limit to max_results
        flat_results = flat_results[:max_results]
        
        # For each result, extract the content
        for result in flat_results:
            if "url" in result and result["url"]:
                try:
                    extracted_content = self.extract_content(result["url"])
                    result["extracted_content"] = extracted_content
                except Exception as e:
                    print(f"Error extracting content from {result['url']}: {str(e)}")
                    result["extracted_content"] = {
                        "error": str(e),
                        "extraction_success": False
                    }
        
        return flat_results
