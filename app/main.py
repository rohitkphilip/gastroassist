from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import langchain
from app.core.query_processor import QueryProcessor
from app.core.reasoning_agent import ReasoningAgent
from app.core.knowledge_router import KnowledgeRouter
from app.output.answer_generator import AnswerGenerator
from app.output.source_compiler import SourceCompiler
from app.output.quality_assurance import QualityAssurance

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
    # Core system pipeline
    query_processor = QueryProcessor()
    reasoning_agent = ReasoningAgent()
    knowledge_router = KnowledgeRouter()
    
    # Output generation pipeline
    answer_generator = AnswerGenerator()
    source_compiler = SourceCompiler()
    quality_assurance = QualityAssurance()
    
    # Process query through the pipeline
    processed_query = query_processor.process(query.text)
    information_needs = reasoning_agent.analyze(processed_query)
    knowledge_results = knowledge_router.retrieve(information_needs)
    
    # Generate response
    answer = answer_generator.generate(knowledge_results, processed_query)
    sources = source_compiler.compile(knowledge_results)
    
    # Use the correct method name: check instead of verify
    quality_results = quality_assurance.check(answer, sources)
    
    # Construct the final response
    response = {
        "answer": answer,
        "sources": sources,
        "confidence_score": quality_results.get("confidence_score", 0.0)
    }
    
    return response

