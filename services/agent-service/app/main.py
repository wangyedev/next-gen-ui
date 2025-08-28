from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import os
from typing import List
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from schemas.requests import QueryRequest, QueryResponse
from schemas.components import AgentResponse
from agents.graph import MultiAgentGraph

agent_graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global agent_graph
    try:
        agent_graph = MultiAgentGraph()
        print("✅ Multi-agent graph initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agent graph: {e}")
        print("Make sure to set your GOOGLE_API_KEY environment variable")
    
    yield
    
    # Shutdown
    # Any cleanup code can go here


app = FastAPI(
    title="Multi-Agent UI System",
    description="LangGraph-based multi-agent system for UI component selection",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Multi-Agent UI System API", "status": "running"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent_graph_initialized": agent_graph is not None
    }


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    if not agent_graph:
        raise HTTPException(
            status_code=500, 
            detail="Agent graph not initialized. Please check your Google API key."
        )
    
    try:
        result: AgentResponse = agent_graph.process_query(
            query=request.query,
            context=request.context,
            schemas=request.schemas
        )
        
        return QueryResponse(
            answer=result.answer,
            component=result.component.model_dump() if result.component else {},
            reasoning=result.reasoning or "",
            success=True,
            error=""
        )
    
    except Exception as e:
        return QueryResponse(
            answer="I apologize, but I encountered an error processing your request.",
            component={},
            reasoning="",
            success=False,
            error=str(e)
        )


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/query")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            if not agent_graph:
                error_response = {
                    "type": "error",
                    "message": "Agent graph not initialized"
                }
                await manager.send_personal_message(
                    json.dumps(error_response), 
                    websocket
                )
                continue
            
            await manager.send_personal_message(
                json.dumps({"type": "status", "message": "Processing query..."}),
                websocket
            )
            
            try:
                result: AgentResponse = await agent_graph.aprocess_query(
                    query=request_data.get("query", ""),
                    context=request_data.get("context", ""),
                    schemas=request_data.get("schemas")
                )
                
                response = {
                    "type": "result",
                    "data": {
                        "answer": result.answer,
                        "component": result.component.model_dump() if result.component else {},
                        "reasoning": result.reasoning or "",
                        "success": True,
                        "error": ""
                    }
                }
                
                await manager.send_personal_message(
                    json.dumps(response),
                    websocket
                )
                
            except Exception as e:
                error_response = {
                    "type": "result",
                    "data": {
                        "answer": "I apologize, but I encountered an error processing your request.",
                        "component": {},
                        "reasoning": "",
                        "success": False,
                        "error": str(e)
                    }
                }
                
                await manager.send_personal_message(
                    json.dumps(error_response),
                    websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
