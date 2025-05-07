#!/usr/bin/env python
"""
Test script for the enhanced GastroAssist pipeline:
Tavily Search -> Tavily Extract -> LLM Summarizer
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to path to import app modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# Import relevant modules
from app.core.query_processor import QueryProcessor
from app.core.reasoning_agent import ReasoningAgent
from app.core.knowledge_router import KnowledgeRouter

def main():
    """Execute a test of the enhanced pipeline"""
    # Load environment variables
    load_dotenv()
    
    # Check for API keys
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not tavily_api_key:
        print("ERROR: TAVILY_API_KEY environment variable is not set")
        print("Please set it in your .env file or environment")
        sys.exit(1)
    
    if not openai_api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set")
        print("Please set it in your .env file or environment")
        sys.exit(1)
    
    print("=== GastroAssist Enhanced Pipeline Test ===")
    print("Tavily Search -> Tavily Extract -> LLM Summarizer")
    print()
    
    # Get test query from command line argument or use default
    if len(sys.argv) > 1:
        test_query = " ".join(sys.argv[1:])
    else:
        test_query = "What are the latest treatment guidelines for H. pylori?"
    
    print(f"Test Query: {test_query}")
    print("\n1. Initializing components...")
    
    # Initialize pipeline components
    query_processor = QueryProcessor()
    reasoning_agent = ReasoningAgent()
    knowledge_router = KnowledgeRouter()
    
    print("\n2. Processing query...")
    processed_query = query_processor.process(test_query)
    print(f"   Processed query: {processed_query}")
    
    print("\n3. Analyzing information needs...")
    information_needs = reasoning_agent.analyze(processed_query)
    print(f"   Identified {len(information_needs)} information needs:")
    for i, need in enumerate(information_needs):
        print(f"   - Need {i+1}: {need['type']} - '{need['query']}' (Priority: {need['priority']})")
    
    print("\n4. Executing knowledge pipeline (search -> extract -> summarize)...")
    print("   This may take a minute...")
    results = knowledge_router.retrieve(information_needs)
    
    print("\n5. Results:")
    for need_key, need_result in results.items():
        print(f"\n   === {need_key.upper()} ===")
        
        # Print raw search results
        if "raw_search_results" in need_result:
            print(f"   Found {len(need_result['raw_search_results'])} search results")
            for i, result in enumerate(need_result['raw_search_results'][:2]):  # Show first 2 only
                print(f"   - Result {i+1}: {result.get('title', 'No title')} ({result.get('url', 'No URL')})")
            if len(need_result['raw_search_results']) > 2:
                print(f"   - ... and {len(need_result['raw_search_results'])-2} more")
        
        # Print extracted content stats
        if "extracted_contents" in need_result:
            print(f"   Extracted content from {len(need_result['extracted_contents'])} sources")
        
        # Print summarized response
        if "summarized_response" in need_result and need_result["summarized_response"]:
            summarized = need_result["summarized_response"]
            print("\n   === SUMMARY ===")
            print(f"   {summarized.get('summary', 'No summary available')}")
            
            if "sources" in summarized and summarized["sources"]:
                print("\n   === SOURCES ===")
                for i, source in enumerate(summarized["sources"]):
                    print(f"   - Source {i+1}: {source.get('title', 'Untitled')} ({source.get('url', 'No URL')})")
    
    print("\n=== Test Complete ===")
    
    # Save results to a JSON file for detailed inspection
    output_dir = os.path.join(parent_dir, "app", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "pipeline_test_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")

if __name__ == "__main__":
    main()
