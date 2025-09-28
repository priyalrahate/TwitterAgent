"""
Agent scheduler for automated tasks and workflows using Fetch.ai
"""
import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import schedule
import threading
from dataclasses import dataclass

from config.settings import Settings
from agent.fetch_ai_client import FetchAIClient


@dataclass
class ScheduledTask:
    """Represents a scheduled task"""
    id: str
    name: str
    task_type: str
    parameters: Dict[str, Any]
    schedule_time: datetime
    interval: Optional[int] = None  # seconds for recurring tasks
    status: str = "scheduled"
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    max_runs: Optional[int] = None


class AgentScheduler:
    """
    Scheduler for automated Twitter agent tasks using Fetch.ai
    """
    
    def __init__(self, agent, settings: Settings):
        self.agent = agent
        self.settings = settings
        self.fetch_ai_client = FetchAIClient(settings)
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.scheduler_thread = None
        
        logger.info("Agent scheduler initialized with Fetch.ai integration")

    async def start(self):
        """Start the scheduler with Fetch.ai integration"""
        if self.running:
            return
        
        # Initialize Fetch.ai client
        await self.fetch_ai_client.initialize_agent()
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Agent scheduler started with Fetch.ai integration")

    async def stop(self):
        """Stop the scheduler and Fetch.ai agent"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        # Stop Fetch.ai agent
        await self.fetch_ai_client.stop_agent()
        
        logger.info("Agent scheduler stopped")

    def _run_scheduler(self):
        """Run the scheduler in a separate thread"""
        while self.running:
            try:
                # Check for tasks that need to run
                current_time = datetime.utcnow()
                
                for task_id, task in list(self.scheduled_tasks.items()):
                    if task.status == "scheduled" and task.schedule_time <= current_time:
                        # Run the task
                        asyncio.create_task(self._execute_scheduled_task(task))
                
                # Sleep for a short interval
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(5)

    async def _execute_scheduled_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        try:
            logger.info(f"Executing scheduled task: {task.name}")
            task.status = "running"
            task.last_run = datetime.utcnow()
            task.run_count += 1
            
            # Execute the task based on type
            if task.task_type == "workflow":
                result = await self._execute_workflow(task.parameters)
            elif task.task_type == "post":
                result = await self._execute_scheduled_post(task.parameters)
            elif task.task_type == "monitor":
                result = await self._execute_monitoring(task.parameters)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            # Update task status
            task.status = "completed"
            
            # Schedule next run if it's a recurring task
            if task.interval and (task.max_runs is None or task.run_count < task.max_runs):
                task.next_run = datetime.utcnow() + timedelta(seconds=task.interval)
                task.status = "scheduled"
                logger.info(f"Task {task.name} scheduled for next run at {task.next_run}")
            else:
                task.status = "finished"
                logger.info(f"Task {task.name} completed (final run)")
            
        except Exception as e:
            logger.error(f"Scheduled task execution failed: {e}")
            task.status = "failed"
            task.error = str(e)

    async def _execute_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow task"""
        workflow_type = parameters.get("type", "")
        
        if workflow_type == "user_monitoring":
            return await self._execute_user_monitoring_workflow(parameters)
        elif workflow_type == "trend_analysis":
            return await self._execute_trend_analysis_workflow(parameters)
        elif workflow_type == "content_curation":
            return await self._execute_content_curation_workflow(parameters)
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

    async def _execute_user_monitoring_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute user monitoring workflow"""
        username = parameters.get("username", "")
        keywords = parameters.get("keywords", [])
        
        # Get user timeline
        tweets = await self.agent.twitter_client.get_user_timeline(
            user_id=parameters.get("user_id", ""),
            max_results=50
        )
        
        # Filter by keywords if provided
        filtered_tweets = tweets
        if keywords:
            filtered_tweets = [
                tweet for tweet in tweets
                if any(keyword.lower() in tweet.get("text", "").lower() for keyword in keywords)
            ]
        
        # Analyze tweets
        if filtered_tweets:
            analysis = await self.agent.gpt_planner.analyze_tweets(filtered_tweets)
        else:
            analysis = {"summary": "No tweets found matching keywords"}
        
        return {
            "workflow_type": "user_monitoring",
            "username": username,
            "tweets_found": len(filtered_tweets),
            "analysis": analysis
        }

    async def _execute_trend_analysis_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trend analysis workflow"""
        topic = parameters.get("topic", "")
        timeframe = parameters.get("timeframe", "24h")
        
        # Search for tweets about the topic
        end_time = datetime.utcnow()
        if timeframe == "24h":
            start_time = end_time - timedelta(hours=24)
        elif timeframe == "7d":
            start_time = end_time - timedelta(days=7)
        else:
            start_time = end_time - timedelta(hours=1)
        
        tweets = await self.agent.twitter_client.search_recent_tweets(
            query=topic,
            max_results=200,
            start_time=start_time,
            end_time=end_time
        )
        
        # Analyze trends
        if tweets:
            trend_analysis = await self.agent.gpt_planner.analyze_trends(tweets, topic, timeframe)
        else:
            trend_analysis = {"trend_summary": "No tweets found for topic"}
        
        return {
            "workflow_type": "trend_analysis",
            "topic": topic,
            "timeframe": timeframe,
            "tweets_analyzed": len(tweets),
            "trend_analysis": trend_analysis
        }

    async def _execute_content_curation_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content curation workflow"""
        topics = parameters.get("topics", [])
        max_tweets = parameters.get("max_tweets", 50)
        
        curated_content = []
        
        for topic in topics:
            tweets = await self.agent.twitter_client.search_recent_tweets(
                query=topic,
                max_results=max_tweets // len(topics)
            )
            
            if tweets:
                # Analyze and rank tweets
                analysis = await self.agent.gpt_planner.analyze_tweets(tweets)
                curated_content.extend(tweets[:5])  # Top 5 tweets per topic
        
        return {
            "workflow_type": "content_curation",
            "topics": topics,
            "curated_tweets": len(curated_content),
            "content": curated_content
        }

    async def _execute_scheduled_post(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scheduled post task"""
        content = parameters.get("content", "")
        
        result = await self.agent.twitter_client.create_tweet(text=content)
        
        return {
            "task_type": "scheduled_post",
            "tweet_id": result["id"],
            "content": content
        }

    async def _execute_monitoring(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute monitoring task"""
        # This would implement specific monitoring logic
        return {
            "task_type": "monitoring",
            "status": "completed"
        }

    async def schedule_workflow(self, workflow_config: Dict[str, Any]) -> str:
        """Schedule a workflow task using Fetch.ai"""
        try:
            # Try to schedule via Fetch.ai first
            if self.fetch_ai_client.is_connected:
                try:
                    task_id = await self.fetch_ai_client.schedule_task(workflow_config)
                    logger.info(f"Workflow scheduled via Fetch.ai: {task_id}")
                    return task_id
                except Exception as e:
                    logger.warning(f"Fetch.ai scheduling failed, using local scheduler: {e}")
            
            # Fallback to local scheduling
            task_id = f"workflow_{len(self.scheduled_tasks)}_{datetime.utcnow().timestamp()}"
            
            task = ScheduledTask(
                id=task_id,
                name=workflow_config.get("name", f"Workflow {task_id}"),
                task_type="workflow",
                parameters=workflow_config,
                schedule_time=datetime.utcnow(),
                interval=workflow_config.get("interval"),
                max_runs=workflow_config.get("max_runs")
            )
            
            self.scheduled_tasks[task_id] = task
            logger.info(f"Workflow scheduled locally: {task.name}")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to schedule workflow: {e}")
            raise

    async def schedule_post(self, content: str, schedule_time: datetime) -> str:
        """Schedule a post for a specific time using Fetch.ai"""
        try:
            # Try to schedule via Fetch.ai first
            if self.fetch_ai_client.is_connected:
                try:
                    post_config = {
                        "type": "scheduled_post",
                        "content": content,
                        "schedule_time": schedule_time.isoformat()
                    }
                    task_id = await self.fetch_ai_client.schedule_task(post_config)
                    logger.info(f"Post scheduled via Fetch.ai for {schedule_time}: {content[:50]}...")
                    return task_id
                except Exception as e:
                    logger.warning(f"Fetch.ai post scheduling failed, using local scheduler: {e}")
            
            # Fallback to local scheduling
            task_id = f"post_{len(self.scheduled_tasks)}_{datetime.utcnow().timestamp()}"
            
            task = ScheduledTask(
                id=task_id,
                name=f"Scheduled Post: {content[:50]}...",
                task_type="post",
                parameters={"content": content},
                schedule_time=schedule_time
            )
            
            self.scheduled_tasks[task_id] = task
            logger.info(f"Post scheduled locally for {schedule_time}: {content[:50]}...")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to schedule post: {e}")
            raise

    async def schedule_recurring_task(self, task_config: Dict[str, Any]) -> str:
        """Schedule a recurring task using Fetch.ai"""
        try:
            # Try to schedule via Fetch.ai first
            if self.fetch_ai_client.is_connected:
                try:
                    recurring_config = {
                        "type": "recurring_task",
                        "task_config": task_config,
                        "interval": task_config.get("interval", 3600),
                        "max_runs": task_config.get("max_runs")
                    }
                    task_id = await self.fetch_ai_client.schedule_task(recurring_config)
                    logger.info(f"Recurring task scheduled via Fetch.ai: {task_id}")
                    return task_id
                except Exception as e:
                    logger.warning(f"Fetch.ai recurring task scheduling failed, using local scheduler: {e}")
            
            # Fallback to local scheduling
            task_id = f"recurring_{len(self.scheduled_tasks)}_{datetime.utcnow().timestamp()}"
            
            task = ScheduledTask(
                id=task_id,
                name=task_config.get("name", f"Recurring Task {task_id}"),
                task_type=task_config.get("type", "workflow"),
                parameters=task_config.get("parameters", {}),
                schedule_time=datetime.utcnow(),
                interval=task_config.get("interval", 3600),
                max_runs=task_config.get("max_runs")
            )
            
            self.scheduled_tasks[task_id] = task
            logger.info(f"Recurring task scheduled locally: {task.name}")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to schedule recurring task: {e}")
            raise

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        if task_id in self.scheduled_tasks:
            task = self.scheduled_tasks[task_id]
            task.status = "cancelled"
            logger.info(f"Task cancelled: {task.name}")
            return True
        return False

    async def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Get all scheduled tasks"""
        return [
            {
                "id": task.id,
                "name": task.name,
                "type": task.task_type,
                "status": task.status,
                "schedule_time": task.schedule_time.isoformat(),
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "run_count": task.run_count,
                "max_runs": task.max_runs
            }
            for task in self.scheduled_tasks.values()
        ]

    async def get_scheduled_count(self) -> int:
        """Get count of scheduled tasks including Fetch.ai tasks"""
        local_count = len([t for t in self.scheduled_tasks.values() if t.status == "scheduled"])
        
        # Get Fetch.ai task count if connected
        if self.fetch_ai_client.is_connected:
            try:
                fetch_status = await self.fetch_ai_client.get_agent_status()
                fetch_count = fetch_status.get("agent_status", {}).get("scheduled_tasks", 0)
                return local_count + fetch_count
            except Exception as e:
                logger.warning(f"Failed to get Fetch.ai task count: {e}")
        
        return local_count

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        task = self.scheduled_tasks.get(task_id)
        if task:
            return {
                "id": task.id,
                "name": task.name,
                "type": task.task_type,
                "status": task.status,
                "schedule_time": task.schedule_time.isoformat(),
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "run_count": task.run_count,
                "max_runs": task.max_runs,
                "error": getattr(task, 'error', None)
            }
        return None
