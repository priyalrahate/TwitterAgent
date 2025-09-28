"""
Workflow manager for loading and executing predefined workflows
"""
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger

from agent.core_agent import TwitterAgent


class WorkflowManager:
    """
    Manages predefined workflows for the Twitter Agent
    """
    
    def __init__(self, agent: TwitterAgent):
        self.agent = agent
        self.workflows_dir = Path("workflows")
        self.loaded_workflows: Dict[str, Dict[str, Any]] = {}
        
        # Load all workflow files
        self._load_workflows()
        
        logger.info(f"Workflow manager initialized with {len(self.loaded_workflows)} workflows")

    def _load_workflows(self):
        """Load all workflow files from the workflows directory"""
        if not self.workflows_dir.exists():
            logger.warning("Workflows directory not found")
            return
        
        for workflow_file in self.workflows_dir.glob("*.json"):
            try:
                with open(workflow_file, 'r') as f:
                    workflow = json.load(f)
                    workflow_name = workflow.get("name", workflow_file.stem)
                    self.loaded_workflows[workflow_name] = workflow
                    logger.info(f"Loaded workflow: {workflow_name}")
            except Exception as e:
                logger.error(f"Failed to load workflow {workflow_file}: {e}")

    def get_workflow(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific workflow by name"""
        return self.loaded_workflows.get(name)

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all available workflows"""
        return [
            {
                "name": name,
                "description": workflow.get("description", ""),
                "type": workflow.get("type", "unknown"),
                "version": workflow.get("version", "1.0.0")
            }
            for name, workflow in self.loaded_workflows.items()
        ]

    async def execute_workflow(self, workflow_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a specific workflow with given parameters"""
        try:
            workflow = self.get_workflow(workflow_name)
            if not workflow:
                raise ValueError(f"Workflow '{workflow_name}' not found")
            
            logger.info(f"Executing workflow: {workflow_name}")
            
            # Merge workflow parameters with provided parameters
            workflow_params = workflow.get("parameters", {})
            if parameters:
                workflow_params.update(parameters)
            
            # Execute workflow steps
            results = await self._execute_workflow_steps(workflow, workflow_params)
            
            # Generate output
            output = self._generate_workflow_output(workflow, results)
            
            return {
                "workflow_name": workflow_name,
                "status": "success",
                "results": results,
                "output": output,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "workflow_name": workflow_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _execute_workflow_steps(self, workflow: Dict[str, Any], parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute all steps in a workflow"""
        steps = workflow.get("steps", [])
        results = []
        
        for step in steps:
            try:
                logger.info(f"Executing step: {step.get('id', 'unknown')}")
                
                # Resolve parameters with template variables
                step_params = self._resolve_parameters(step.get("parameters", {}), parameters, results)
                
                # Execute the step
                step_result = await self._execute_step(step, step_params)
                
                results.append({
                    "step_id": step.get("id"),
                    "action": step.get("action"),
                    "status": "success",
                    "result": step_result
                })
                
            except Exception as e:
                logger.error(f"Step execution failed: {e}")
                results.append({
                    "step_id": step.get("id"),
                    "action": step.get("action"),
                    "status": "error",
                    "error": str(e)
                })
                
                # Check if step is required
                if step.get("required", True):
                    raise e
        
        return results

    async def _execute_step(self, step: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        action = step.get("action")
        
        # Map workflow actions to agent methods
        if action == "search_tweets":
            return await self.agent.search_tweets(
                query=parameters.get("query", ""),
                max_results=parameters.get("max_results", 100),
                start_time=parameters.get("start_time"),
                end_time=parameters.get("end_time")
            )
        elif action == "get_user_timeline":
            return await self.agent.twitter_client.get_user_timeline(
                user_id=parameters.get("user_id", ""),
                max_results=parameters.get("max_results", 100)
            )
        elif action == "analyze_sentiment":
            tweets = parameters.get("tweets", [])
            return await self.agent.gpt_planner.analyze_tweets(tweets)
        elif action == "create_tweet":
            return await self.agent.twitter_client.create_tweet(
                text=parameters.get("text", "")
            )
        elif action == "like_tweet":
            return await self.agent.twitter_client.like_tweet(
                tweet_id=parameters.get("tweet_id", "")
            )
        elif action == "retweet":
            return await self.agent.twitter_client.retweet(
                tweet_id=parameters.get("tweet_id", "")
            )
        elif action == "follow_user":
            return await self.agent.twitter_client.follow_user(
                user_id=parameters.get("user_id", "")
            )
        elif action == "get_trends":
            return await self.agent.twitter_client.get_trending_topics(
                woeid=parameters.get("woeid", 1)
            )
        else:
            raise ValueError(f"Unknown action: {action}")

    def _resolve_parameters(self, step_params: Dict[str, Any], workflow_params: Dict[str, Any], 
                          previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve template parameters in step parameters"""
        resolved = {}
        
        for key, value in step_params.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Template variable
                var_name = value[2:-2]
                
                # Check if it's a previous step result
                if "." in var_name:
                    step_id, field = var_name.split(".", 1)
                    for result in previous_results:
                        if result["step_id"] == step_id:
                            resolved[key] = result["result"].get(field)
                            break
                else:
                    # Workflow parameter
                    resolved[key] = workflow_params.get(var_name, value)
            else:
                resolved[key] = value
        
        return resolved

    def _generate_workflow_output(self, workflow: Dict[str, Any], results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate workflow output based on results"""
        output_config = workflow.get("output", {})
        output_fields = output_config.get("fields", [])
        
        output = {}
        for field in output_fields:
            # Extract field value from results
            for result in results:
                if field in result["result"]:
                    output[field] = result["result"][field]
                    break
        
        return output

    async def schedule_workflow(self, workflow_name: str, parameters: Dict[str, Any] = None, 
                              schedule_config: Dict[str, Any] = None) -> str:
        """Schedule a workflow for recurring execution"""
        try:
            workflow = self.get_workflow(workflow_name)
            if not workflow:
                raise ValueError(f"Workflow '{workflow_name}' not found")
            
            # Create schedule configuration
            if not schedule_config:
                schedule_config = workflow.get("schedule", {})
            
            # Schedule the workflow
            task_id = await self.agent.scheduler.schedule_workflow({
                "name": f"{workflow_name} - {datetime.utcnow().isoformat()}",
                "type": "workflow",
                "workflow_name": workflow_name,
                "parameters": parameters or {},
                "interval": schedule_config.get("interval"),
                "max_runs": schedule_config.get("max_runs")
            })
            
            logger.info(f"Workflow '{workflow_name}' scheduled with ID: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to schedule workflow: {e}")
            raise

    async def get_workflow_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a scheduled workflow"""
        return await self.agent.scheduler.get_task_status(task_id)

    async def cancel_workflow(self, task_id: str) -> bool:
        """Cancel a scheduled workflow"""
        return await self.agent.scheduler.cancel_task(task_id)
