#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\web_search_mcp\server_fastapi_backup.py #api #python #source_code #web_interface  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\web_search_mcp\server_fastapi_backup.py #api #python #source_code #web_interface  
**Category:** Source Code  
**Status:** Active

import json
import time
import logging
import datetime
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from utils.search import perform_search
from utils.citation import generate_citations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("web-search-mcp")

# Load configuration
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    config = {
        "server": {"host": "0.0.0.0", "port": 8765},
        "search": {"default_num_results": 5, "max_num_results": 10},
        "rate_limit": {"requests_per_minute": 10}
    }

# Initialize FastAPI
app = FastAPI(
    title="Web Search MCP Server",
    description="MCP server for web search with citations",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting implementation
class RateLimiter:
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
    
    def is_rate_limited(self) -> bool:
        current_time = time.time()
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        if len(self.request_times) >= self.requests_per_minute:
            return True
        
        self.request_times.append(current_time)
        return False

rate_limiter = RateLimiter(config["rate_limit"]["requests_per_minute"])

# Define request/response models
class SearchRequest(BaseModel):
    query: str = Field(..., description="The search query")
    num_results: Optional[int] = Field(
        default=config["search"]["default_num_results"],
        le=config["search"]["max_num_results"],
        description="Number of results to return"
    )
    require_citations: Optional[bool] = Field(
        default=True,
        description="Whether to generate citations for results"
    )

class SearchResult(BaseModel):
    title: str
    content: str
    url: str
    citation: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
    metadata: Dict[str, Any]

# Define API endpoints
@app.get("/")
async def root():
    return {
        "name": "Web Search MCP Server",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    # Check rate limit
    if rate_limiter.is_rate_limited():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    logger.info(f"Search request received: {request.query}")
    
    try:
        # Perform the search
        search_results = await perform_search(
            query=request.query,
            num_results=request.num_results,
            safe_search=config["search"]["safe_search"],
            timeout=config["search"]["timeout"]
        )
        
        # Generate citations if required
        if request.require_citations:
            search_results = await generate_citations(search_results)
        
        # Create response
        response = SearchResponse(
            results=search_results,
            metadata={
                "query": request.query,
                "timestamp": datetime.datetime.now().isoformat(),
                "result_count": len(search_results)
            }
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error processing search: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info(f"Starting Web Search MCP Server on {config['server']['host']}:{config['server']['port']}")
    uvicorn.run(
        "server:app", 
        host=config["server"]["host"], 
        port=config["server"]["port"],
        reload=config["server"].get("debug", False)
    )
