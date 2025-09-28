"""
Core Twitter Agent with Fetch.ai integration
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass

from config.settings import settings
from agent.gpt_planner import GPTPlanner
from agent.twitter_client import TwitterClient
from agent.workflow_executor import WorkflowExecutor
from agent.scheduler import AgentScheduler


@dataclass
class AgentTask:
    """Represents a task for the Twitter agent"""
    id: str
    type: str
    parameters: Dict[str, Any]
    status: str = "pending"
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class TwitterAgent:
    """
    Main Twitter Agent orchestrator that coordinates between:
    - GPT Planner (task planning and analysis)
    - Twitter Client (API operations)
    - Workflow Executor (task execution)
    - Scheduler (automated tasks)
    """
    
    def __init__(self):
        self.gpt_planner = GPTPlanner()
        self.twitter_client = TwitterClient()
        self.workflow_executor = WorkflowExecutor(self.twitter_client)
        self.scheduler = AgentScheduler(self, settings)
        
        # Task management
        self.active_tasks: Dict[str, AgentTask] = {}
        self.task_history: List[AgentTask] = []
        
        logger.info("Twitter Agent initialized successfully")

    async def process_natural_language_request(self, request: str) -> Dict[str, Any]:
        """
        Process a natural language request and execute the corresponding tasks
        """
        try:
            logger.info(f"Processing request: {request}")
            
            # Step 1: Use GPT to plan the task
            task_plan = await self.gpt_planner.plan_task(request)
            logger.info(f"Generated task plan: {task_plan}")
            
            # Step 2: Create agent tasks
            tasks = self._create_tasks_from_plan(task_plan)
            
            # Step 3: Execute tasks
            results = await self._execute_tasks(tasks)
            
            # Step 4: Generate final response using GPT
            final_response = await self.gpt_planner.generate_response(request, results)
            
            return {
                "status": "success",
                "request": request,
                "tasks_executed": len(tasks),
                "results": results,
                "response": final_response
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "status": "error",
                "request": request,
                "error": str(e)
            }

    def _create_tasks_from_plan(self, plan: Dict[str, Any]) -> List[AgentTask]:
        """Convert GPT plan into executable agent tasks"""
        tasks = []
        
        for step in plan.get("steps", []):
            task = AgentTask(
                id=f"task_{len(self.active_tasks)}_{datetime.utcnow().timestamp()}",
                type=step["action"],
                parameters=step["parameters"]
            )
            tasks.append(task)
            self.active_tasks[task.id] = task
            
        return tasks

    async def _execute_tasks(self, tasks: List[AgentTask]) -> List[Dict[str, Any]]:
        """Execute a list of agent tasks"""
        results = []
        
        for task in tasks:
            try:
                logger.info(f"Executing task: {task.type}")
                task.status = "running"
                
                # Execute the task using workflow executor
                result = await self.workflow_executor.execute_task(task)
                
                task.status = "completed"
                task.completed_at = datetime.utcnow()
                task.result = result
                
                results.append({
                    "task_id": task.id,
                    "type": task.type,
                    "status": "success",
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Task execution failed: {str(e)}")
                task.status = "failed"
                task.error = str(e)
                
                results.append({
                    "task_id": task.id,
                    "type": task.type,
                    "status": "error",
                    "error": str(e)
                })
            
            # Move completed task to history
            self.task_history.append(task)
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
        
        return results

    async def search_tweets(self, query: str, max_results: int = 100, 
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Search for tweets with specified parameters"""
        try:
            tweets = await self.twitter_client.search_recent_tweets(
                query=query,
                max_results=min(max_results, settings.MAX_TWEETS_PER_REQUEST),
                start_time=start_time,
                end_time=end_time
            )
            
            # Analyze tweets using GPT
            analysis = await self.gpt_planner.analyze_tweets(tweets)
            
            return {
                "query": query,
                "tweet_count": len(tweets),
                "tweets": tweets,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Tweet search failed: {str(e)}")
            raise

    async def monitor_user(self, username: str, keywords: List[str] = None,
                          schedule_interval: int = None) -> str:
        """Set up monitoring for a specific user"""
        try:
            # Create monitoring workflow
            workflow_config = {
                "type": "user_monitoring",
                "username": username,
                "keywords": keywords or [],
                "interval": schedule_interval or settings.DEFAULT_SCHEDULE_INTERVAL
            }
            
            # Schedule the monitoring task
            task_id = await self.scheduler.schedule_workflow(workflow_config)
            
            logger.info(f"User monitoring scheduled for @{username}")
            return task_id
            
        except Exception as e:
            logger.error(f"User monitoring setup failed: {str(e)}")
            raise

    async def analyze_trends(self, topic: str, timeframe: str = "24h") -> Dict[str, Any]:
        """Analyze trends for a specific topic"""
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            if timeframe == "24h":
                start_time = end_time - timedelta(hours=24)
            elif timeframe == "7d":
                start_time = end_time - timedelta(days=7)
            else:
                start_time = end_time - timedelta(hours=1)
            
            # Search for tweets
            search_result = await self.search_tweets(
                query=topic,
                max_results=500,
                start_time=start_time,
                end_time=end_time
            )
            
            # Generate trend analysis
            trend_analysis = await self.gpt_planner.analyze_trends(
                search_result["tweets"],
                topic,
                timeframe
            )
            
            return {
                "topic": topic,
                "timeframe": timeframe,
                "tweet_count": search_result["tweet_count"],
                "trend_analysis": trend_analysis,
                "raw_data": search_result
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {str(e)}")
            raise

    async def create_automated_post(self, content: str, schedule_time: Optional[datetime] = None) -> str:
        """Create and optionally schedule a post"""
        try:
            if schedule_time:
                # Schedule the post
                task_id = await self.scheduler.schedule_post(content, schedule_time)
                logger.info(f"Post scheduled for {schedule_time}")
                return task_id
            else:
                # Post immediately
                result = await self.twitter_client.create_tweet(text=content)
                logger.info(f"Post created successfully: {result['id']}")
                return result['id']
                
        except Exception as e:
            logger.error(f"Post creation failed: {str(e)}")
            raise

    async def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of the agent"""
        return {
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.task_history),
            "scheduled_workflows": await self.scheduler.get_scheduled_count(),
            "last_activity": max([t.created_at for t in self.task_history], default=None),
            "status": "running"
        }

    async def start_scheduler(self):
        """Start the agent scheduler"""
        await self.scheduler.start()
        logger.info("Agent scheduler started")

    async def stop_scheduler(self):
        """Stop the agent scheduler"""
        await self.scheduler.stop()
        logger.info("Agent scheduler stopped")

    async def cleanup(self):
        """Cleanup resources"""
        await self.stop_scheduler()
        await self.twitter_client.close()
        logger.info("Agent cleanup completed")
