"""
Test cases for Twitter Agent
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from agent.core_agent import TwitterAgent, AgentTask
from agent.gpt_planner import GPTPlanner
from agent.twitter_client import TwitterClient
from agent.workflow_executor import WorkflowExecutor
from agent.scheduler import AgentScheduler


class TestTwitterAgent:
    """Test cases for TwitterAgent class"""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing"""
        with patch('agent.core_agent.GPTPlanner'), \
             patch('agent.core_agent.TwitterClient'), \
             patch('agent.core_agent.WorkflowExecutor'), \
             patch('agent.core_agent.AgentScheduler'):
            agent = TwitterAgent()
            return agent
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, mock_agent):
        """Test agent initialization"""
        assert mock_agent is not None
        assert mock_agent.active_tasks == {}
        assert mock_agent.task_history == []
    
    @pytest.mark.asyncio
    async def test_process_natural_language_request(self, mock_agent):
        """Test natural language request processing"""
        # Mock GPT planner response
        mock_agent.gpt_planner.plan_task = AsyncMock(return_value={
            "intent": "Search for tweets",
            "steps": [
                {
                    "action": "search_tweets",
                    "parameters": {"query": "test"},
                    "description": "Search tweets"
                }
            ]
        })
        
        # Mock workflow executor
        mock_agent.workflow_executor.execute_task = AsyncMock(return_value={
            "task_id": "test_task",
            "type": "search_tweets",
            "status": "success",
            "result": {"tweets": []}
        })
        
        # Mock GPT response generation
        mock_agent.gpt_planner.generate_response = AsyncMock(return_value="Test response")
        
        result = await mock_agent.process_natural_language_request("Find tweets about AI")
        
        assert result["status"] == "success"
        assert result["tasks_executed"] == 1
        assert "response" in result
    
    @pytest.mark.asyncio
    async def test_search_tweets(self, mock_agent):
        """Test tweet search functionality"""
        # Mock Twitter client
        mock_agent.twitter_client.search_recent_tweets = AsyncMock(return_value=[
            {"id": "1", "text": "Test tweet", "author_id": "user1"}
        ])
        
        # Mock GPT analyzer
        mock_agent.gpt_planner.analyze_tweets = AsyncMock(return_value={
            "summary": "Test analysis",
            "sentiment": {"overall": "positive"}
        })
        
        result = await mock_agent.search_tweets("test query", max_results=10)
        
        assert result["query"] == "test query"
        assert result["tweet_count"] == 1
        assert "analysis" in result
    
    @pytest.mark.asyncio
    async def test_analyze_trends(self, mock_agent):
        """Test trend analysis functionality"""
        # Mock search tweets
        mock_agent.search_tweets = AsyncMock(return_value={
            "tweet_count": 50,
            "tweets": [{"id": "1", "text": "Test"}],
            "analysis": {"summary": "Test"}
        })
        
        # Mock GPT trend analysis
        mock_agent.gpt_planner.analyze_trends = AsyncMock(return_value={
            "trend_summary": "Test trend",
            "trend_direction": "rising"
        })
        
        result = await mock_agent.analyze_trends("test topic", "24h")
        
        assert result["topic"] == "test topic"
        assert result["timeframe"] == "24h"
        assert "trend_analysis" in result
    
    @pytest.mark.asyncio
    async def test_monitor_user(self, mock_agent):
        """Test user monitoring functionality"""
        # Mock scheduler
        mock_agent.scheduler.schedule_workflow = AsyncMock(return_value="task_123")
        
        result = await mock_agent.monitor_user("testuser", ["keyword1"], 3600)
        
        assert result == "task_123"
        mock_agent.scheduler.schedule_workflow.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_automated_post(self, mock_agent):
        """Test automated post creation"""
        # Mock Twitter client
        mock_agent.twitter_client.create_tweet = AsyncMock(return_value={"id": "tweet_123"})
        
        result = await mock_agent.create_automated_post("Test content")
        
        assert result == "tweet_123"
        mock_agent.twitter_client.create_tweet.assert_called_once_with(text="Test content")
    
    @pytest.mark.asyncio
    async def test_get_agent_status(self, mock_agent):
        """Test agent status retrieval"""
        # Mock scheduler
        mock_agent.scheduler.get_scheduled_count = AsyncMock(return_value=5)
        
        result = await mock_agent.get_agent_status()
        
        assert "active_tasks" in result
        assert "completed_tasks" in result
        assert "scheduled_workflows" in result
        assert result["scheduled_workflows"] == 5


class TestGPTPlanner:
    """Test cases for GPTPlanner class"""
    
    @pytest.fixture
    def mock_planner(self):
        """Create a mock GPT planner for testing"""
        with patch('agent.gpt_planner.openai.AsyncOpenAI'):
            planner = GPTPlanner()
            return planner
    
    @pytest.mark.asyncio
    async def test_plan_task(self, mock_planner):
        """Test task planning functionality"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"intent": "Test", "steps": []}'
        
        mock_planner.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await mock_planner.plan_task("test request")
        
        assert "intent" in result
        assert "steps" in result
    
    @pytest.mark.asyncio
    async def test_analyze_tweets(self, mock_planner):
        """Test tweet analysis functionality"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"summary": "Test", "sentiment": {"overall": "positive"}}'
        
        mock_planner.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        tweets = [{"id": "1", "text": "Test tweet"}]
        result = await mock_planner.analyze_tweets(tweets)
        
        assert "summary" in result
        assert "sentiment" in result
    
    @pytest.mark.asyncio
    async def test_generate_tweet_content(self, mock_planner):
        """Test tweet content generation"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test tweet content"
        
        mock_planner.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await mock_planner.generate_tweet_content("test topic")
        
        assert result == "Test tweet content"


class TestTwitterClient:
    """Test cases for TwitterClient class"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Twitter client for testing"""
        with patch('agent.twitter_client.tweepy.Client'), \
             patch('agent.twitter_client.httpx.AsyncClient'):
            client = TwitterClient()
            return client
    
    @pytest.mark.asyncio
    async def test_search_recent_tweets(self, mock_client):
        """Test recent tweet search"""
        # Mock Tweepy response
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].data = {"id": "1", "text": "Test tweet"}
        mock_response.data[0].author_id = "user1"
        mock_response.includes = {"users": []}
        
        mock_client.client.search_recent_tweets = Mock(return_value=mock_response)
        
        result = await mock_client.search_recent_tweets("test query")
        
        assert len(result) == 1
        assert result[0]["id"] == "1"
    
    @pytest.mark.asyncio
    async def test_create_tweet(self, mock_client):
        """Test tweet creation"""
        # Mock Tweepy response
        mock_response = Mock()
        mock_response.data = {"id": "tweet_123"}
        
        mock_client.client.create_tweet = Mock(return_value=mock_response)
        
        result = await mock_client.create_tweet("Test content")
        
        assert result["id"] == "tweet_123"
    
    @pytest.mark.asyncio
    async def test_like_tweet(self, mock_client):
        """Test tweet liking"""
        # Mock Tweepy response
        mock_response = Mock()
        mock_response.data = {"liked": True}
        
        mock_client.client.like = Mock(return_value=mock_response)
        
        result = await mock_client.like_tweet("tweet_123")
        
        assert result is True


class TestWorkflowExecutor:
    """Test cases for WorkflowExecutor class"""
    
    @pytest.fixture
    def mock_executor(self):
        """Create a mock workflow executor for testing"""
        with patch('agent.workflow_executor.TwitterClient'):
            executor = WorkflowExecutor(Mock())
            return executor
    
    @pytest.mark.asyncio
    async def test_execute_task(self, mock_executor):
        """Test task execution"""
        # Mock task
        task = AgentTask(
            id="test_task",
            type="search_tweets",
            parameters={"query": "test"}
        )
        
        # Mock handler
        mock_executor._handle_search_tweets = AsyncMock(return_value={"tweets": []})
        
        result = await mock_executor.execute_task(task)
        
        assert result["status"] == "success"
        assert result["task_id"] == "test_task"
    
    @pytest.mark.asyncio
    async def test_handle_search_tweets(self, mock_executor):
        """Test search tweets handler"""
        # Mock Twitter client
        mock_executor.twitter_client.search_recent_tweets = AsyncMock(return_value=[
            {"id": "1", "text": "Test"}
        ])
        
        params = {"query": "test", "max_results": 10}
        result = await mock_executor._handle_search_tweets(params)
        
        assert result["query"] == "test"
        assert result["tweet_count"] == 1


class TestAgentScheduler:
    """Test cases for AgentScheduler class"""
    
    @pytest.fixture
    def mock_scheduler(self):
        """Create a mock scheduler for testing"""
        scheduler = AgentScheduler(Mock())
        return scheduler
    
    @pytest.mark.asyncio
    async def test_schedule_workflow(self, mock_scheduler):
        """Test workflow scheduling"""
        workflow_config = {
            "name": "Test Workflow",
            "type": "workflow",
            "parameters": {"test": "value"}
        }
        
        task_id = await mock_scheduler.schedule_workflow(workflow_config)
        
        assert task_id is not None
        assert task_id in mock_scheduler.scheduled_tasks
    
    @pytest.mark.asyncio
    async def test_schedule_post(self, mock_scheduler):
        """Test post scheduling"""
        content = "Test post content"
        schedule_time = datetime.utcnow() + timedelta(hours=1)
        
        task_id = await mock_scheduler.schedule_post(content, schedule_time)
        
        assert task_id is not None
        assert task_id in mock_scheduler.scheduled_tasks
    
    @pytest.mark.asyncio
    async def test_cancel_task(self, mock_scheduler):
        """Test task cancellation"""
        # Schedule a task first
        workflow_config = {"name": "Test", "type": "workflow"}
        task_id = await mock_scheduler.schedule_workflow(workflow_config)
        
        # Cancel the task
        result = await mock_scheduler.cancel_task(task_id)
        
        assert result is True
        assert mock_scheduler.scheduled_tasks[task_id].status == "cancelled"


# Integration tests
class TestIntegration:
    """Integration test cases"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        with patch('agent.core_agent.GPTPlanner'), \
             patch('agent.core_agent.TwitterClient'), \
             patch('agent.core_agent.WorkflowExecutor'), \
             patch('agent.core_agent.AgentScheduler'):
            
            agent = TwitterAgent()
            
            # Mock all dependencies
            agent.gpt_planner.plan_task = AsyncMock(return_value={
                "intent": "Test workflow",
                "steps": [{"action": "search_tweets", "parameters": {"query": "test"}}]
            })
            
            agent.workflow_executor.execute_task = AsyncMock(return_value={
                "task_id": "test",
                "status": "success",
                "result": {"tweets": []}
            })
            
            agent.gpt_planner.generate_response = AsyncMock(return_value="Test response")
            
            # Test the complete workflow
            result = await agent.process_natural_language_request("Find tweets about AI")
            
            assert result["status"] == "success"
            assert result["tasks_executed"] == 1


if __name__ == "__main__":
    pytest.main([__file__])
