import os
import requests
import json
from dotenv import load_dotenv

def test_tavily_api():
    """Test the Tavily API connection and key validity"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get the API key
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("ERROR: TAVILY_API_KEY environment variable is not set")
        print("Please add your Tavily API key to the .env file:")
        print("TAVILY_API_KEY=your_api_key_here")
        return False
    
    # Print API key (first 5 chars only for security)
    api_key_preview = api_key[:5] + "..." if len(api_key) > 5 else "***"
    print(f"Using Tavily API key: {api_key_preview}")
    
    # Prepare request headers and payload
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    payload = {
        "query": "test query",
        "search_depth": "basic",
        "include_answer": False,
        "include_images": False,
        "include_raw_content": False,
        "max_results": 1
    }
    
    # Make the API request
    try:
        print("Making test request to Tavily API...")
        response = requests.post(
            "https://api.tavily.com/search",
            headers=headers,
            json=payload
        )
        
        # Print response status
        print(f"Tavily API response status: {response.status_code}")
        
        # If we get an error response, print more details
        if response.status_code != 200:
            print(f"Tavily API error: {response.text}")
            
            if response.status_code == 401:
                print("\nERROR: Your Tavily API key is invalid or expired.")
                print("Please check your API key at https://tavily.com/dashboard")
                print("Make sure you've signed up and created an API key.")
                print("Then update your .env file with the new key.")
            return False
        
        # Parse the response
        data = response.json()
        
        # Check if we got results
        if "results" in data and len(data["results"]) > 0:
            print("\nSUCCESS: Tavily API is working correctly!")
            print(f"Found {len(data['results'])} results for test query")
            return True
        else:
            print("\nWARNING: Tavily API returned no results")
            print("This might be normal for a test query, but check if your account has search credits")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"\nERROR: Failed to connect to Tavily API: {str(e)}")
        print("Please check your internet connection and try again")
        return False
    except json.JSONDecodeError as e:
        print(f"\nERROR: Failed to parse Tavily API response: {str(e)}")
        return False
    except Exception as e:
        print(f"\nERROR: Unexpected error testing Tavily API: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_tavily_api()
    if success:
        print("\nYou can now use the Tavily search in your application")
    else:
        print("\nPlease fix the Tavily API issues before continuing")