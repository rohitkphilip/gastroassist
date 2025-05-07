# GastroAssist Enhanced Pipeline Documentation

## Overview

This document describes the implementation of the enhanced GastroAssist knowledge retrieval pipeline, which follows the sequence:

**Tavily Search → Tavily Extract → LLM Summarizer**

The pipeline is designed to deliver brief, crisp, and medically accurate responses to gastroenterology queries, with proper source attribution.

## Architecture Flow

![Enhanced GastroAssist Pipeline Flow](../../static/gastroassist-pipeline-diagram.svg)

## Pipeline Components

### 1. Query Processing Phase

#### User Query
- Entry point for clinical gastroenterology queries
- Raw text input from healthcare professionals

#### Query Processor
- Normalizes and preprocesses the query text
- Identifies key medical terms and concepts
- Prepares the query for further analysis

#### Reasoning Agent
- Analyzes the query to determine information needs
- Uses specialized medical knowledge base (conditions, procedures, medications)
- Identifies query intent (treatment, diagnosis, screening, etc.)
- Formulates optimized search queries with medical context

#### Knowledge Router
- Coordinates the entire pipeline execution
- Routes queries to appropriate knowledge sources
- Manages the flow between search, extraction, and summarization

### 2. Knowledge Retrieval Phase

#### Tavily Search
- Specialized search component for medical information
- Configures search parameters based on query type
- Prioritizes medical domains and sources

#### Tavily Search API
- External search API provided by Tavily
- Optimized for comprehensive search results
- Returns structured search results with metadata

#### Raw Search Results
- Unprocessed search results from Tavily API
- Contains titles, snippets, URLs, and relevance scores
- Provides the foundation for further content extraction

#### Best URLs
- Selected subset of highest-ranking search results
- Filtered based on relevance score and domain quality
- Targeted for full content extraction

### 3. Content Processing Phase

#### Tavily Extract
- Content extraction component for medical web pages
- Uses specialized approach for handling medical content
- Implements error handling and fallback mechanisms

#### Tavily Search API with Raw Content
- Uses the Tavily Search API with `include_raw_content: true`
- Configured to retrieve complete article content
- Alternative to dedicated extraction API (which is unavailable)

#### Extracted Content
- Full-text content from medical sources
- Comprehensive information beyond search snippets
- Provides rich context for accurate summarization

#### Content Filtering
- Validates and processes extracted content
- Handles edge cases (empty content, excessive length)
- Prepares content for efficient summarization

### 4. Response Generation Phase

#### LLM Summarizer (GPT-3.5 Turbo)
- Natural language processing component
- Uses OpenAI's GPT-3.5 Turbo model for cost-efficiency
- Implements robust error handling and fallback responses

#### Medical Prompt
- Specialized instructions for LLM summarization
- Emphasizes brevity, factual accuracy, and citation
- Optimized for medical content summarization

#### Concise Summary
- Brief, factual summary of medical information
- Properly cited with source attributions
- Focused on answering the original query

#### API Response
- Final structured response for the frontend
- Contains the summary, sources, and metadata
- Ready for presentation to healthcare professionals

## Implementation Details

### 1. Tavily Search Implementation

The search component uses Tavily's API to find relevant medical information:

```python
# Key components of Tavily Search
def search(self, query: str, search_depth: str = "basic", filter_medical: bool = True):
    # Configure search parameters
    payload = {
        "query": query,
        "search_depth": search_depth,
        "include_answer": False,
        "include_images": False,
        "max_results": 5,
        "api_key": self.api_key
    }
    
    # Add medical filter if requested
    if filter_medical:
        payload["search_filters"] = {
            "include_domains": [
                "pubmed.ncbi.nlm.nih.gov",
                "mayoclinic.org",
                "medlineplus.gov",
                "nejm.org",
                # Additional medical domains...
            ]
        }
    
    # Make API request and process results
    # ...
```

### 2. Tavily Extract Implementation

The extraction component uses Tavily's Search API with raw content parameters to extract full-text content:

```python
# Key components of Tavily Extract
def extract(self, url: str):
    # Configure extraction parameters using Search API
    payload = {
        "query": f"Extract information from {url}",
        "search_depth": "advanced",
        "include_raw_content": True,
        "include_domains": [url.split('//')[-1].split('/')[0]],
        "max_results": 1,
        "api_key": self.api_key
    }
    
    # Process API response to extract content
    # ...
    
    # Implement multi-tiered fallback strategy
    # 1. Tavily API with raw content
    # 2. Direct HTML extraction
    # 3. Basic URL information
    # ...
```

### 3. LLM Summarizer Implementation

The summarizer component uses OpenAI's GPT-3.5 Turbo model with specialized medical prompting:

```python
# Key components of LLM Summarizer
def summarize(self, query: str, extracted_contents: List[Dict[str, Any]]):
    # Validate extracted contents
    valid_contents = [content for content in extracted_contents 
                     if content.get("extraction_success", False) and content.get("content")]
    
    # Prepare context from validated contents
    context = self._prepare_context(valid_contents)
    
    # Create specialized medical prompt
    prompt = f"""
    As a gastroenterology expert, provide a concise, accurate response to this query:

    QUERY: {query}

    Below are sources from medical literature. Use these to formulate your response.

    {context}

    INSTRUCTIONS:
    1. Only include medical facts directly supported by the sources
    2. Be brief and crisp - focus on the most relevant information
    3. Use clear medical terminology for healthcare professionals
    4. Cite sources using [SOURCE X] notation after each fact
    5. If sources conflict, present both perspectives
    6. If information is limited, state this clearly
    7. Avoid personal opinions or unsupported recommendations
    8. Use bullet points for readability when appropriate
    9. Keep your response to 3-7 sentences for straightforward queries
    10. Focus on the direct answer to the query
    """
    
    # Generate summary using OpenAI API
    # ...
    
    # Process and return results with comprehensive error handling
    # ...
```

## Error Handling and Robustness

The enhanced pipeline implements comprehensive error handling at multiple levels:

### 1. Search-Level Error Handling
- Handles API authentication failures
- Provides fallback search results when API fails
- Implements automatic retries for transient failures

### 2. Extraction-Level Error Handling
- Multi-tiered extraction approach:
  - Primary: Tavily API with raw content
  - Secondary: Direct HTML extraction
  - Fallback: Basic URL information
- Validates extracted content before processing
- Handles malformed URLs and inaccessible websites

### 3. Summarization-Level Error Handling
- Validates extracted contents before summarization
- Handles empty or invalid content scenarios
- Provides appropriate fallback responses
- Implements null-safety checks throughout
- Ensures consistent response structure even in error cases

## Configuration Requirements

### Required Environment Variables:
```
# Tavily API key for search and extraction
TAVILY_API_KEY=your_tavily_api_key

# OpenAI API key for GPT-3.5 Turbo summarization
OPENAI_API_KEY=your_openai_api_key
```

### Optional Configuration:
```
# Debug mode for detailed logging (default: False)
DEBUG=True

# Maximum sources to extract (default: 3)
MAX_EXTRACT_SOURCES=5

# Maximum tokens for summarization (default: 500)
MAX_SUMMARY_TOKENS=700
```

## Testing the Pipeline

A test script is provided to validate the entire pipeline:

```bash
# Run with default test query
python scripts/test_pipeline.py

# Run with custom query
python scripts/test_pipeline.py "What are the latest guidelines for H. pylori treatment?"
```

The test script outputs detailed information about each stage of the pipeline and saves complete results to a JSON file for inspection.

## Performance Considerations

- **API Rate Limits**: Be aware of Tavily and OpenAI API rate limits
- **Extraction Timeouts**: Content extraction may time out for large pages
- **Context Window Limits**: GPT-3.5 Turbo has a smaller context window than GPT-4
- **Error Recovery**: The pipeline continues with fallbacks in case of component failures

## Future Improvements

1. **Parallel Processing**: Implement concurrent extraction of multiple URLs
2. **Caching Layer**: Add caching of search and extraction results
3. **Content Filtering**: Implement more sophisticated content relevance filtering
4. **Alternative Extractors**: Support additional extraction methods
5. **User Feedback Loop**: Incorporate feedback to improve pipeline quality
