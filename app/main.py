from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging

from app.core.query_processor import QueryProcessor
from app.core.reasoning_agent import ReasoningAgent
from app.core.knowledge_router import KnowledgeRouter
from app.output.answer_generator import AnswerGenerator
from app.output.source_compiler import SourceCompiler
from app.output.quality_assurance import QualityAssurance
from app.output.llm_summarizer import LLMSummarizer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GastroAssist AI API")

class Query(BaseModel):
    text: str
    user_id: str
    context: Optional[dict] = None

class Source(BaseModel):
    title: str
    url: Optional[str] = None
    snippet: str
    confidence: float

class Response(BaseModel):
    answer: str
    sources: List[Source]
    confidence_score: float

@app.get("/")
async def root():
    """
    Root endpoint that provides basic API information and health status
    """
    return {
        "name": "GastroAssist AI API",
        "status": "online",
        "version": "0.1.0",
        "documentation": "/docs",
        "health": "ok"
    }

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Serve favicon.ico file
    """
    # Check if favicon exists in the static directory
    favicon_path = "static/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    else:
        # Return an empty response if favicon doesn't exist
        return Response(content=b"", media_type="image/x-icon")

@app.post("/api/query", response_model=Response)
async def process_query(query: Query):
    """
    Process a gastroenterology query using the enhanced pipeline:
    Tavily Search -> Tavily Extract -> LLM Summarizer
    """
    try:
        logger.info(f"Processing query: {query.text}")
        
        # Initialize pipeline components
        query_processor = QueryProcessor()
        reasoning_agent = ReasoningAgent()
        knowledge_router = KnowledgeRouter()
        quality_assurance = QualityAssurance()
        
        # Step 1: Process query to understand intent and extract medical concepts
        processed_query = query_processor.process(query.text)
        logger.info(f"Processed query: {processed_query}")
        
        # Step 2: Analyze the query to determine information needs
        information_needs = reasoning_agent.analyze(processed_query)
        logger.info(f"Identified information needs: {len(information_needs)} items")
        
        # Step 3: Retrieve knowledge using enhanced pipeline (search -> extract -> summarize)
        # The knowledge_router now handles the entire pipeline internally
        knowledge_results = knowledge_router.retrieve(information_needs)
        logger.info(f"Retrieved knowledge for {len(knowledge_results)} information needs")
        
        # Step 4: Compile sources from the knowledge results
        sources = []
        answer = ""
        
        # Extract summarized response and sources from the knowledge results
        for need_key, need_result in knowledge_results.items():
            if "summarized_response" in need_result and need_result["summarized_response"]:
                summarized_response = need_result["summarized_response"]
                
                # Use the summarized text as the answer
                if "summary" in summarized_response and summarized_response["summary"]:
                    answer = summarized_response["summary"]
                
                # Compile sources from the summarized response
                if "sources" in summarized_response and summarized_response["sources"]:
                    for source in summarized_response["sources"]:
                        sources.append({
                            "title": source.get("title", "Unknown Source"),
                            "url": source.get("url", ""),
                            "snippet": source.get("snippet", ""),
                            "confidence": source.get("confidence", 0.8)
                        })
        
        # If no answer was generated, provide a fallback
        if not answer:
            answer = "I'm sorry, but I couldn't find specific information to answer your query about gastroenterology. Please try reformulating your question or contact a healthcare professional for medical advice."
        
        # Step 5: Check quality of the generated answer
        quality_results = quality_assurance.check(answer, sources)
        confidence_score = quality_results.get("confidence_score", 0.0)
        
        # Step 6: Construct the final response
        response = {
            "answer": answer,
            "sources": sources,
            "confidence_score": confidence_score
        }
        
        logger.info(f"Successfully processed query with confidence score: {confidence_score}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/api/query/direct", response_model=Dict[str, Any])
async def direct_query(query: Query):
    """
    Direct query endpoint that returns the full pipeline results
    including search results, extracted content, and the summarized response
    """
    try:
        # Initialize the knowledge router with the enhanced pipeline
        knowledge_router = KnowledgeRouter()
        
        # Use the convenience method to run the full pipeline on a single query
        result = knowledge_router.search_extract_summarize(query.text)
        
        return {
            "query": query.text,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error processing direct query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
