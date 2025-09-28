"""
Fetch.ai AEA agent integration for Twitter Agent
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

try:
    import aea
    from aea.agent import Agent
    from aea.configurations.base import ConnectionConfig, ProtocolConfig
    from aea.connections.http import HttpConnection
    from aea.protocols.base import Message
    from aea.skills.base import Skill
    FETCH_AI_AVAILABLE = True
except ImportError:
    FETCH_AI_AVAILABLE = False
    logger.warning("Fetch.ai AEA modules not available, using mock implementation")

from config.settings import Settings


class FetchAIClient:
    """
    Fetch.ai AEA client for autonomous agent operations
    """
    
    def __init__(self, settings: Settings):
        self.agent = None
        self.agent_id = settings.FETCH_AI_AGENT_ID
        self.api_key = settings.FETCH_AI_API_KEY
        self.is_connected = False
        self.settings = settings
        
        if not FETCH_AI_AVAILABLE:
            logger.warning("Fetch.ai AEA modules not available, using mock implementation")
        
        logger.info("Fetch.ai client initialized")

    async def initialize_agent(self):
        """Initialize the AEA agent"""
        try:
            if not FETCH_AI_AVAILABLE or not self.api_key or not self.agent_id:
                logger.warning("Fetch.ai not available or credentials not configured, using mock mode")
                return await self._initialize_mock_agent()
            
            # Create AEA agent configuration
            agent_config = {
                "name": "twitter_agent",
                "author": "twitter_agent_author",
                "version": "0.1.0",
                "description": "Twitter automation agent",
                "aea_version": "1.0.0",
                "license": "Apache-2.0",
                "fingerprint": {},
                "fingerprint_ignore_patterns": [],
                "connections": ["http"],
                "contracts": [],
                "protocols": ["default"],
                "skills": ["twitter_automation"],
                "behaviours": {},
                "handlers": {},
                "models": {},
                "dependencies": {},
                "build_entrypoint": None,
                "run_entrypoint": None,
            }
            
            # Initialize the agent
            self.agent = Agent.from_config(agent_config)
            
            # Add HTTP connection for API calls
            http_config = ConnectionConfig(
                name="http",
                author="fetchai",
                version="1.0.0",
                type_="http",
                config={"api_spec_path": None},
            )
            
            self.agent.resources.add_connection(http_config)
            
            # Start the agent
            await self.agent.start()
            self.is_connected = True
            
            logger.info("Fetch.ai agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Fetch.ai agent: {e}")
            # Fallback to mock mode
            return await self._initialize_mock_agent()

    async def _initialize_mock_agent(self):
        """Initialize mock agent for development/testing"""
        self.agent = MockFetchAIAgent()
        self.is_connected = True
        logger.info("Fetch.ai mock agent initialized")

    async def schedule_task(self, task_config: Dict[str, Any]) -> str:
        """Schedule a task using Fetch.ai agent"""
        try:
            if not self.is_connected:
                await self.initialize_agent()
            
            # Create task message
            task_message = {
                "task_id": f"task_{datetime.utcnow().timestamp()}",
                "type": "schedule_task",
                "config": task_config,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to Fetch.ai agent
            result = await self.agent.schedule_task(task_message)
            
            logger.info(f"Task scheduled via Fetch.ai: {result['task_id']}")
            return result['task_id']
            
        except Exception as e:
            logger.error(f"Failed to schedule task via Fetch.ai: {e}")
            raise

    async def execute_autonomous_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an autonomous workflow using Fetch.ai"""
        try:
            if not self.is_connected:
                await self.initialize_agent()
            
            # Create workflow message
            workflow_message = {
                "workflow_id": f"workflow_{datetime.utcnow().timestamp()}",
                "type": "autonomous_workflow",
                "config": workflow_config,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Execute via Fetch.ai agent
            result = await self.agent.execute_workflow(workflow_message)
            
            logger.info(f"Autonomous workflow executed via Fetch.ai: {result['workflow_id']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute workflow via Fetch.ai: {e}")
            raise

    async def get_agent_status(self) -> Dict[str, Any]:
        """Get Fetch.ai agent status"""
        try:
            if not self.is_connected:
                return {"status": "disconnected", "agent_id": None}
            
            status = await self.agent.get_status()
            return {
                "status": "connected",
                "agent_id": self.agent_id,
                "agent_status": status
            }
            
        except Exception as e:
            logger.error(f"Failed to get Fetch.ai agent status: {e}")
            return {"status": "error", "error": str(e)}

    async def stop_agent(self):
        """Stop the Fetch.ai agent"""
        try:
            if self.agent and self.is_connected:
                await self.agent.stop()
                self.is_connected = False
                logger.info("Fetch.ai agent stopped")
        except Exception as e:
            logger.error(f"Failed to stop Fetch.ai agent: {e}")


class MockFetchAIAgent:
    """Mock Fetch.ai agent for development/testing"""
    
    def __init__(self):
        self.scheduled_tasks = {}
        self.workflows = {}
        self.status = "running"
    
    async def schedule_task(self, task_message: Dict[str, Any]) -> Dict[str, Any]:
        """Mock task scheduling"""
        task_id = task_message["task_id"]
        self.scheduled_tasks[task_id] = {
            "config": task_message["config"],
            "status": "scheduled",
            "created_at": task_message["timestamp"]
        }
        
        # Simulate task execution
        asyncio.create_task(self._simulate_task_execution(task_id))
        
        return {"task_id": task_id, "status": "scheduled"}
    
    async def execute_workflow(self, workflow_message: Dict[str, Any]) -> Dict[str, Any]:
        """Mock workflow execution"""
        workflow_id = workflow_message["workflow_id"]
        self.workflows[workflow_id] = {
            "config": workflow_message["config"],
            "status": "running",
            "created_at": workflow_message["timestamp"]
        }
        
        # Simulate workflow execution
        asyncio.create_task(self._simulate_workflow_execution(workflow_id))
        
        return {"workflow_id": workflow_id, "status": "running"}
    
    async def get_status(self) -> Dict[str, Any]:
        """Mock status"""
        return {
            "status": self.status,
            "scheduled_tasks": len(self.scheduled_tasks),
            "active_workflows": len([w for w in self.workflows.values() if w["status"] == "running"])
        }
    
    async def stop(self):
        """Mock stop"""
        self.status = "stopped"
    
    async def _simulate_task_execution(self, task_id: str):
        """Simulate task execution"""
        await asyncio.sleep(2)  # Simulate processing time
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks[task_id]["status"] = "completed"
            self.scheduled_tasks[task_id]["completed_at"] = datetime.utcnow().isoformat()
    
    async def _simulate_workflow_execution(self, workflow_id: str):
        """Simulate workflow execution"""
        await asyncio.sleep(5)  # Simulate processing time
        if workflow_id in self.workflows:
            self.workflows[workflow_id]["status"] = "completed"
            self.workflows[workflow_id]["completed_at"] = datetime.utcnow().isoformat()
