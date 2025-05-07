from typing import Dict, Any
import os
import requests
import json
from dotenv import load_dotenv

class TavilyExtract:
    """
    Integration with Tavily API for content extraction from medical URLs
    """
    
    def __init__(self):
        """Initialize the Tavily extraction connector"""
        # Load environment variables from .env file
        load_dotenv()
        
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY environment variable is not set")
        # We will use the main Tavily search endpoint with specific parameters for content
        self.base_url = "https://api.tavily.com/search"
    
    def extract(self, url: str) -> Dict[str, Any]:
        """
        Extract content from a URL using the Tavily API
        
        Args:
            url: The URL to extract content from
            
        Returns:
            Dictionary containing extracted content
        """
        # Prepare request headers and payload
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
        
        # Use Tavily search API with include_raw_content=True to get full content
        # and the specific URL as the search query
        payload = {
            "query": f"Extract information from {url}",
            "search_depth": "advanced",
            "include_raw_content": True,  # This will get the full content
            "include_domains": [url.split('//')[-1].split('/')[0]],  # Limit to this domain
            "max_results": 1,  # Only need one result since we're targeting a specific URL
            "api_key": self.api_key
        }
        
        try:
            # Debug info - print API key (first 5 chars only for security)
            api_key_preview = self.api_key[:5] + "..." if self.api_key else "None"
            print(f"Using Tavily API key: {api_key_preview}")
            
            # Print request URL and payload for debugging (mask API key)
            debug_payload = {**payload}
            if "api_key" in debug_payload:
                debug_payload["api_key"] = "***masked***"
            print(f"Request URL: {self.base_url}")
            print(f"Request payload: {json.dumps(debug_payload)}")
            
            # Make the API request
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload
            )
            
            # Print response status for debugging
            print(f"Tavily Extract API response status: {response.status_code}")
            
            # If we get an error response, print more details
            if response.status_code != 200:
                print(f"Tavily Extract API error: {response.text}")
                
                # If unauthorized, provide more helpful message
                if response.status_code == 401:
                    print("Tavily API key is invalid or expired. Please check your API key at https://tavily.com/dashboard")
                    return self._get_fallback_extract(url)
                # If it's a validation error, show more helpful message
                elif response.status_code == 422:
                    print("Tavily API validation error. Check that the URL is valid and publicly accessible.")
                    return self._get_fallback_extract(url)
                elif response.status_code == 404:
                    print("Tavily API endpoint not found. The API structure may have changed.")
                    return self._get_fallback_extract(url)
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Extract content from search results
            content = ""
            title = ""
            
            if "results" in data and data["results"]:
                result = data["results"][0]  # Take the first result
                
                # Get title
                title = result.get("title", "")
                
                # Get content
                if "raw_content" in result:
                    content = result["raw_content"]
                elif "content" in result:
                    content = result["content"]
                
                # If we have at least title or content, consider it a successful extraction
                if title or content:
                    return {
                        "title": title,
                        "content": content,
                        "author": "",  # Tavily doesn't provide author info
                        "published_date": "",  # Tavily doesn't provide date info
                        "source_url": url,
                        "extraction_success": True
                    }
            
            # If we couldn't extract content, fall back
            print(f"No content extracted from Tavily API response. Response: {json.dumps(data)[:200]}...")
            return self._use_alternative_extraction(url)
            
        except requests.exceptions.RequestException as e:
            # Log the error (in a production system, use proper logging)
            print(f"Error making Tavily Extract API request: {str(e)}")
            
            # Return fallback results in case of error
            return self._use_alternative_extraction(url)
        except json.JSONDecodeError as e:
            # Log the error (in a production system, use proper logging)
            print(f"Error parsing Tavily Extract API response: {str(e)}")
            
            # Return fallback results in case of error
            return self._use_alternative_extraction(url)
        except Exception as e:
            # Log the error (in a production system, use proper logging)
            print(f"Unexpected error in Tavily extract: {str(e)}")
            
            # Return fallback results in case of error
            return self._use_alternative_extraction(url)
    
    def _use_alternative_extraction(self, url: str) -> Dict[str, Any]:
        """
        Use an alternative extraction method when Tavily API fails
        
        Args:
            url: The URL to extract content from
            
        Returns:
            Dictionary with extracted content
        """
        print(f"Attempting alternative extraction for URL: {url}")
        
        try:
            # Make a simple GET request to the URL
            response = requests.get(url, timeout=10)
            
            # Check if request was successful
            if response.status_code == 200:
                # We could implement a simple HTML parser here to extract content
                # For now, we'll just use the raw HTML with a warning
                content = f"[NOTE: Extracted with basic method. Content may include HTML markup.]\n\n{response.text[:5000]}..."
                
                # Extract a basic title from the URL
                url_path = url.split("/")[-1].replace("-", " ").replace("_", " ")
                if "." in url_path:
                    url_path = url_path.split(".")[0]  # Remove file extension
                title = url_path.title() if url_path else f"Content from {url}"
                
                return {
                    "title": title,
                    "content": content,
                    "author": "Unknown",
                    "published_date": "",
                    "source_url": url,
                    "extraction_success": True,
                    "extraction_method": "basic"
                }
            else:
                print(f"Alternative extraction failed with status code: {response.status_code}")
                return self._get_fallback_extract(url)
                
        except Exception as e:
            print(f"Error in alternative extraction: {str(e)}")
            return self._get_fallback_extract(url)
    
    def _get_fallback_extract(self, url: str) -> Dict[str, Any]:
        """
        Generate fallback extraction results when all extraction methods fail
        
        Args:
            url: The URL that was attempted to be extracted
            
        Returns:
            Dictionary with fallback content
        """
        print(f"Using fallback extraction for URL: {url}")
        
        # Try to fetch basic information without the Tavily API
        try:
            # Make a simple HEAD request to check if the URL is accessible
            head_response = requests.head(url, timeout=5)
            is_accessible = head_response.status_code < 400
        except:
            is_accessible = False
        
        # Create a basic fallback result
        domain = url.split("//")[-1].split("/")[0]
        
        # Try to intelligently guess the title from the URL
        url_path = url.split("/")[-1].replace("-", " ").replace("_", " ")
        if "." in url_path:
            url_path = url_path.split(".")[0]  # Remove file extension
        
        title = url_path.title() if url_path else f"Content from {domain}"
        
        fallback_content = "Unable to extract full content from this URL."
        
        if not is_accessible:
            fallback_content += " The URL may be invalid or the website might be inaccessible currently."
        else:
            fallback_content += " Please visit the source directly for complete information."
        
        # Add the URL itself as content so at least we have something
        fallback_content += f"\n\nSource URL: {url}"
        
        return {
            "title": title,
            "content": fallback_content,
            "author": "Unknown",
            "published_date": "",
            "source_url": url,
            "extraction_success": False,
            "fallback": True
        }
        
    def check_api_status(self) -> Dict[str, Any]:
        """
        Check the status of the Tavily API and API key
        
        Returns:
            Dictionary with status information
        """
        try:
            # Use the search endpoint to check status
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
            }
            
            # Simple query to test the API
            payload = {
                "query": "test",
                "max_results": 1,
                "api_key": self.api_key
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    "status": "ok",
                    "message": "API connection successful",
                    "api_key_valid": True
                }
            else:
                return {
                    "status": "error",
                    "message": f"API test failed with status {response.status_code}: {response.text}",
                    "api_key_valid": False
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"API test failed: {str(e)}",
                "api_key_valid": False
            }
