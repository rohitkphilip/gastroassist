from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from app.knowledge.dynamic_search import DynamicSearch
from app.output.llm_summarizer import LLMSummarizer

class KnowledgeRouter:
    """
    Routes information needs to appropriate knowledge sources and processes the results
    using enhanced pipeline: Tavily Search -> Tavily Extract -> LLM Summarizer
    """
    
    def __init__(self):
        """Initialize the knowledge router"""
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize search components
        self.dynamic_search = DynamicSearch()
        
        # Initialize LLM summarizer
        self.summarizer = LLMSummarizer()
    
    def retrieve(self, information_needs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Retrieve information based on the identified needs using the enhanced pipeline
        
        Args:
            information_needs: List of information needs
            
        Returns:
            Dictionary containing retrieved and processed knowledge
        """
        results = {}
        
        # Process each information need through the enhanced pipeline
        for need in information_needs:
            need_type = need.get("type", "general")
            query = need.get("query", "")
            
            # Prepare container for this specific need
            need_result = {
                "query": query,
                "type": need_type,
                "raw_search_results": [],
                "extracted_contents": [],
                "summarized_response": None
            }
            
            # Step 1: Perform the search based on need type
            if need_type == "medical":
                search_type = "medical"
            else:
                search_type = "general"
                
            search_results = self.dynamic_search.search(query, search_type=search_type)
            
            # Get the appropriate result list based on need type
            result_list = []
            if need_type == "medical" and "medical" in search_results:
                result_list = search_results["medical"]
            elif need_type == "general" and "general" in search_results:
                result_list = search_results["general"]
            
            # Store raw search results
            need_result["raw_search_results"] = result_list
            
            # Step 2: Extract content from top search results (max 3 for efficiency)
            extracted_contents = []
            for i, result in enumerate(result_list[:3]):  # Limit to top 3 results
                if "url" in result and result["url"]:
                    try:
                        # Use Tavily extract for content extraction
                        extracted_content = self.dynamic_search.extract_content(result["url"], extractor="tavily")
                        extracted_contents.append(extracted_content)
                    except Exception as e:
                        print(f"Error extracting content from {result['url']}: {str(e)}")
                        # Add basic info without full content
                        extracted_contents.append({
                            "title": result.get("title", "Unknown"),
                            "content": result.get("snippet", "Content extraction failed"),
                            "source_url": result.get("url", ""),
                            "extraction_success": False,
                            "error": str(e)
                        })
            
            # Store extracted contents
            need_result["extracted_contents"] = extracted_contents
            
            # Step 3: Use LLM to summarize with medical-specific prompt
            if extracted_contents:
                try:
                    summary = self.summarizer.summarize(query, extracted_contents)
                    need_result["summarized_response"] = summary
                except Exception as e:
                    print(f"Error in summarization: {str(e)}")
                    need_result["summarized_response"] = {
                        "summary": f"Unable to generate summary: {str(e)}",
                        "sources": [],
                        "error": str(e)
                    }
            else:
                need_result["summarized_response"] = {
                    "summary": "No relevant information found for your query.",
                    "sources": [],
                    "error": "No content to summarize"
                }
            
            # Add this processed need to the overall results
            results[f"need_{len(results)}"] = need_result
        
        return results
    
    def search_extract_summarize(self, query: str, search_type: str = "medical") -> Dict[str, Any]:
        """
        Convenience method to run the full pipeline on a single query
        
        Args:
            query: The search query
            search_type: Type of search to perform (medical or general)
            
        Returns:
            Processed result with summary and sources
        """
        # Create a single information need
        information_needs = [{
            "type": search_type,
            "query": query
        }]
        
        # Run the full pipeline
        results = self.retrieve(information_needs)
        
        # Return the first result (since we only had one query)
        if results and "need_0" in results:
            return results["need_0"]
        else:
            return {
                "query": query,
                "type": search_type,
                "raw_search_results": [],
                "extracted_contents": [],
                "summarized_response": {
                    "summary": "Processing pipeline failed to produce results.",
                    "sources": [],
                    "error": "Pipeline failure"
                }
            }
