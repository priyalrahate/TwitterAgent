"""
Main entry point for Twitter Agent
"""
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys

from agent.core_agent import TwitterAgent
from workflows.workflow_manager import WorkflowManager
from config.settings import settings
from api.gemini_routes import router as gemini_router

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    "logs/agent.log",
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="1 day",
    retention="30 days"
)

# Global agent instance
agent = None
workflow_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global agent, workflow_manager
    
    # Startup
    logger.info("Starting Twitter Agent...")
    
    try:
        # Initialize agent
        agent = TwitterAgent()
        workflow_manager = WorkflowManager(agent)
        
        # Start scheduler
        await agent.start_scheduler()
        
        logger.info("Twitter Agent started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Twitter Agent...")
        if agent:
            await agent.cleanup()
        logger.info("Twitter Agent shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Twitter Agent API",
    description="AI-powered Twitter automation agent with Fetch.ai and ChatGPT integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Gemini router
app.include_router(gemini_router)

# API Routes

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Twitter Agent API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    status = await agent.get_agent_status()
    return {
        "status": "healthy",
        "agent": status
    }

# Agent Management Endpoints

@app.get("/api/agent/status")
async def get_agent_status():
    """Get agent status"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        status = await agent.get_agent_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/start")
async def start_agent():
    """Start the agent"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        await agent.start_scheduler()
        status = await agent.get_agent_status()
        return {"message": "Agent started", "status": status}
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/stop")
async def stop_agent():
    """Stop the agent"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        await agent.stop_scheduler()
        status = await agent.get_agent_status()
        return {"message": "Agent stopped", "status": status}
    except Exception as e:
        logger.error(f"Failed to stop agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Natural Language Processing Endpoints

@app.post("/api/agent/process")
async def process_request(request: dict):
    """Process natural language request"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        user_request = request.get("request", "")
        if not user_request:
            raise HTTPException(status_code=400, detail="Request text is required")
        
        result = await agent.process_natural_language_request(user_request)
        return result
    except Exception as e:
        logger.error(f"Failed to process request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Twitter Operations Endpoints

@app.post("/api/twitter/search")
async def search_tweets(request: dict):
    """Search for tweets"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        query = request.get("query", "")
        max_results = request.get("max_results", 100)
        start_time = request.get("start_time")
        end_time = request.get("end_time")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        result = await agent.search_tweets(
            query=query,
            max_results=max_results,
            start_time=start_time,
            end_time=end_time
        )
        return result
    except Exception as e:
        logger.error(f"Failed to search tweets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/twitter/analyze-trends")
async def analyze_trends(request: dict):
    """Analyze trends for a topic"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        topic = request.get("topic", "")
        timeframe = request.get("timeframe", "24h")
        
        if not topic:
            raise HTTPException(status_code=400, detail="Topic is required")
        
        result = await agent.analyze_trends(topic, timeframe)
        return result
    except Exception as e:
        logger.error(f"Failed to analyze trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/twitter/monitor-user")
async def monitor_user(request: dict):
    """Set up user monitoring"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        username = request.get("username", "")
        keywords = request.get("keywords", [])
        schedule_interval = request.get("schedule_interval")
        
        if not username:
            raise HTTPException(status_code=400, detail="Username is required")
        
        task_id = await agent.monitor_user(username, keywords, schedule_interval)
        return {"message": "User monitoring started", "task_id": task_id}
    except Exception as e:
        logger.error(f"Failed to monitor user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/twitter/create-post")
async def create_post(request: dict):
    """Create a new post"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        content = request.get("content", "")
        schedule_time = request.get("schedule_time")
        
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        result = await agent.create_automated_post(content, schedule_time)
        return {"message": "Post created", "post_id": result}
    except Exception as e:
        logger.error(f"Failed to create post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Workflow Management Endpoints

@app.get("/api/workflows")
async def list_workflows():
    """List all available workflows"""
    if not workflow_manager:
        raise HTTPException(status_code=503, detail="Workflow manager not initialized")
    
    try:
        workflows = workflow_manager.list_workflows()
        return workflows
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/execute")
async def execute_workflow(request: dict):
    """Execute a workflow"""
    if not workflow_manager:
        raise HTTPException(status_code=503, detail="Workflow manager not initialized")
    
    try:
        workflow_name = request.get("workflow_name", "")
        parameters = request.get("parameters", {})
        
        if not workflow_name:
            raise HTTPException(status_code=400, detail="Workflow name is required")
        
        result = await workflow_manager.execute_workflow(workflow_name, parameters)
        return result
    except Exception as e:
        logger.error(f"Failed to execute workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/schedule")
async def schedule_workflow(request: dict):
    """Schedule a workflow"""
    if not workflow_manager:
        raise HTTPException(status_code=503, detail="Workflow manager not initialized")
    
    try:
        workflow_name = request.get("workflow_name", "")
        parameters = request.get("parameters", {})
        schedule_config = request.get("schedule_config", {})
        
        if not workflow_name:
            raise HTTPException(status_code=400, detail="Workflow name is required")
        
        task_id = await workflow_manager.schedule_workflow(
            workflow_name, parameters, schedule_config
        )
        return {"message": "Workflow scheduled", "task_id": task_id}
    except Exception as e:
        logger.error(f"Failed to schedule workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows/status/{task_id}")
async def get_workflow_status(task_id: str):
    """Get workflow status"""
    if not workflow_manager:
        raise HTTPException(status_code=503, detail="Workflow manager not initialized")
    
    try:
        status = await workflow_manager.get_workflow_status(task_id)
        if not status:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return status
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/cancel/{task_id}")
async def cancel_workflow(task_id: str):
    """Cancel a workflow"""
    if not workflow_manager:
        raise HTTPException(status_code=503, detail="Workflow manager not initialized")
    
    try:
        success = await workflow_manager.cancel_workflow(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return {"message": "Workflow cancelled"}
    except Exception as e:
        logger.error(f"Failed to cancel workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Task Management Endpoints

@app.get("/api/tasks")
async def get_tasks():
    """Get all tasks"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Get active tasks
        active_tasks = list(agent.active_tasks.values())
        # Get recent completed tasks
        recent_tasks = agent.task_history[-20:]  # Last 20 tasks
        
        return {
            "active_tasks": [
                {
                    "id": task.id,
                    "type": task.type,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "parameters": task.parameters
                }
                for task in active_tasks
            ],
            "recent_tasks": [
                {
                    "id": task.id,
                    "type": task.type,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "error": task.error
                }
                for task in recent_tasks
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )

if __name__ == "__main__":
    # Create logs directory
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
