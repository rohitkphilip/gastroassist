# Frontend-Backend Integration

## Overview

This document describes the integration between the GastroAssist frontend (built with Next.js) and backend (built with FastAPI), with a focus on the data flow and communication patterns.

![Frontend-Backend Integration](../../static/gastroassist-frontend-backend-integration.svg)

## Integration Architecture

The GastroAssist application follows a clear separation of concerns between the frontend and backend components, connected through a RESTful API interface.

### Frontend Components (Next.js/React)

The frontend is built using Next.js and React with TypeScript, providing a responsive and interactive user interface for healthcare professionals.

#### Key Frontend Components:

1. **QueryInput.tsx**
   - Allows users to input gastroenterology queries
   - Handles form validation and submission
   - Manages query history and suggestions

2. **ResponseDisplay.tsx**
   - Renders AI-generated responses with formatting
   - Highlights key medical terminology
   - Supports source citation display

3. **SourcesList.tsx**
   - Displays cited medical sources
   - Provides links to original publications
   - Shows source confidence scores

4. **LoadingIndicator.tsx**
   - Provides visual feedback during API calls
   - Indicates progress through pipeline stages

5. **Frontend State Management (Redux)**
   - Manages application state
   - Handles caching of queries and responses
   - Provides session persistence

### Backend Components (FastAPI)

The backend is built using FastAPI, providing high-performance API endpoints that process queries through the enhanced knowledge pipeline.

#### Key Backend Components:

1. **FastAPI Endpoints**
   - `/api/query`: Main endpoint for processing gastroenterology queries
   - `/api/query/direct`: Advanced endpoint with full pipeline results

2. **Core Pipeline**
   - Knowledge Router: Orchestrates the pipeline flow
   - Query Processor: Normalizes and analyzes user queries
   - Reasoning Agent: Determines information needs

3. **Enhanced Pipeline**
   - Tavily Search: Finds relevant medical information
   - Tavily Extract: Retrieves full content from search results
   - LLM Summarizer: Generates concise, accurate summaries

4. **Response Generation**
   - Creates structured responses with proper citations
   - Formats content for frontend consumption
   - Includes confidence scores and metadata

## Data Flow

The typical data flow between frontend and backend follows these steps:

1. **User Input → Backend Request**
   - User enters a query in the QueryInput component
   - Frontend creates a structured JSON payload
   - React component dispatches an HTTP POST request to `/api/query`

2. **Backend Processing**
   - FastAPI endpoint receives and validates the request
   - Query processed through the enhanced pipeline
   - External APIs called as needed (Tavily, OpenAI)
   - Structured response generated with citations

3. **Backend Response → Frontend Rendering**
   - Backend returns JSON response with answer and sources
   - Frontend receives and processes the response
   - Redux store updates with the new data
   - ResponseDisplay component renders the answer
   - SourcesList component displays the citations
   - LoadingIndicator is hidden

## API Contract

### Query Request

```json
{
  "text": "What are the latest guidelines for H. pylori treatment?",
  "user_id": "user-12345",
  "context": {
    "patient_age": 45,
    "patient_history": ["previous H. pylori infection", "peptic ulcer disease"],
    "preferred_sources": ["AGA", "ACG"]
  }
}
```

### Query Response

```json
{
  "answer": "Current guidelines for H. pylori treatment recommend quadruple therapy as first-line treatment in most regions due to increasing clarithromycin resistance. The ACG and AGA recommend bismuth quadruple therapy (PPI, bismuth, tetracycline, and metronidazole) for 14 days. In regions with low clarithromycin resistance, triple therapy with a PPI, clarithromycin, and amoxicillin or metronidazole may still be used. Post-treatment testing to confirm eradication is recommended.",
  "sources": [
    {
      "title": "ACG Clinical Guidelines: Treatment of Helicobacter pylori Infection",
      "url": "https://journals.lww.com/ajg/Fulltext/2017/02000/ACG_Clinical_Guideline__Treatment_of_Helicobacter.12.aspx",
      "snippet": "The ACG now recommends bismuth quadruple therapy as first-line treatment in areas with high clarithromycin resistance...",
      "confidence": 0.95
    },
    {
      "title": "AGA Clinical Practice Update on the Management of Helicobacter pylori Infection",
      "url": "https://www.gastrojournal.org/article/S0016-5085(17)35531-2/fulltext",
      "snippet": "For first-line treatment, clinicians should use clarithromycin triple therapy only in regions where clarithromycin resistance is low...",
      "confidence": 0.92
    }
  ],
  "confidence_score": 0.93
}
```

## Error Handling

The frontend-backend integration includes comprehensive error handling:

1. **Frontend Error Handling**
   - Request timeouts with automatic retries
   - User-friendly error messages
   - Fallback UI for failed requests

2. **Backend Error Handling**
   - Detailed logging for debugging
   - Structured error responses
   - Graceful degradation with fallback results

3. **API Error Responses**
```json
{
  "error": {
    "code": "PROCESSING_ERROR",
    "message": "Unable to process your query at this time",
    "details": "Error during content extraction phase"
  }
}
```

## Implementation Details

### Frontend Implementation

```typescript
// Example Redux action for query submission
export const submitQuery = createAsyncThunk(
  'query/submit',
  async (queryData, { rejectWithValue }) => {
    try {
      const response = await axios.post('/api/query', {
        text: queryData.text,
        user_id: 'current-user',
        context: queryData.context || {}
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || {
        error: {
          code: 'NETWORK_ERROR',
          message: 'Unable to connect to the server'
        }
      });
    }
  }
);
```

### Backend Implementation

```python
@app.post("/api/query", response_model=Response)
async def process_query(query: Query):
    """
    Process a gastroenterology query using the enhanced pipeline:
    Tavily Search → Tavily Extract → LLM Summarizer
    """
    try:
        # Initialize pipeline components
        query_processor = QueryProcessor()
        reasoning_agent = ReasoningAgent()
        knowledge_router = KnowledgeRouter()
        
        # Process query through the enhanced pipeline
        processed_query = query_processor.process(query.text)
        information_needs = reasoning_agent.analyze(processed_query)
        knowledge_results = knowledge_router.retrieve(information_needs)
        
        # Extract response from knowledge results
        sources = []
        answer = ""
        
        # Get the summarized response
        for need_key, need_result in knowledge_results.items():
            if "summarized_response" in need_result:
                summarized_response = need_result["summarized_response"]
                
                # Use the summarized text as the answer
                if "summary" in summarized_response:
                    answer = summarized_response["summary"]
                
                # Compile sources
                if "sources" in summarized_response:
                    for source in summarized_response["sources"]:
                        sources.append({
                            "title": source.get("title", "Unknown Source"),
                            "url": source.get("url", ""),
                            "snippet": source.get("snippet", ""),
                            "confidence": source.get("confidence", 0.8)
                        })
        
        # Return the response
        return {
            "answer": answer,
            "sources": sources,
            "confidence_score": 0.93
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={
                "error": {
                    "code": "PROCESSING_ERROR",
                    "message": "Error processing query",
                    "details": str(e)
                }
            }
        )
```

## Security Considerations

1. **API Security**
   - All requests should use HTTPS
   - API keys should be transmitted securely in headers
   - Input validation to prevent injection attacks

2. **Data Privacy**
   - No PHI (Protected Health Information) should be transmitted
   - Queries and responses are not persistently stored by default
   - User IDs are anonymized for analytics purposes

3. **Error Handling Security**
   - Error messages don't expose internal implementation details
   - Stack traces are never returned to the frontend
   - Failed authentication attempts are logged and monitored
