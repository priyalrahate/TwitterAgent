"""
Test script for Fetch.ai and Composio integrations
"""
import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agent.fetch_ai_client import FetchAIClient
from agent.composio_client import ComposioClient
from agent.core_agent import TwitterAgent


async def test_fetch_ai_integration():
    """Test Fetch.ai integration"""
    print("🤖 Testing Fetch.ai Integration")
    print("=" * 50)
    
    fetch_client = FetchAIClient()
    
    try:
        # Initialize Fetch.ai agent
        await fetch_client.initialize_agent()
        print("✅ Fetch.ai agent initialized")
        
        # Test agent status
        status = await fetch_client.get_agent_status()
        print(f"📊 Agent status: {status}")
        
        # Test task scheduling
        task_config = {
            "type": "test_task",
            "name": "Test Task",
            "parameters": {"test": "value"}
        }
        
        task_id = await fetch_client.schedule_task(task_config)
        print(f"📅 Task scheduled: {task_id}")
        
        # Test autonomous workflow
        workflow_config = {
            "type": "test_workflow",
            "name": "Test Workflow",
            "steps": ["step1", "step2"]
        }
        
        result = await fetch_client.execute_autonomous_workflow(workflow_config)
        print(f"⚙️ Workflow executed: {result}")
        
        # Stop agent
        await fetch_client.stop_agent()
        print("🛑 Fetch.ai agent stopped")
        
    except Exception as e:
        print(f"❌ Fetch.ai test failed: {e}")


async def test_composio_integration():
    """Test Composio integration"""
    print("\n🔧 Testing Composio Integration")
    print("=" * 50)
    
    composio_client = ComposioClient()
    
    try:
        # Initialize Composio client
        await composio_client.initialize()
        print("✅ Composio client initialized")
        
        # Test tweet search
        tweets = await composio_client.search_tweets("AI", max_results=5)
        print(f"🔍 Found {len(tweets)} tweets via Composio")
        
        # Test user lookup
        user_data = await composio_client.get_user_by_username("elonmusk")
        print(f"👤 User data retrieved: {user_data.get('username', 'Unknown')}")
        
        # Test trending topics
        trends = await composio_client.get_trending_topics()
        print(f"📈 Retrieved {len(trends)} trending topics")
        
        # Test tweet creation (commented out to avoid actual posting)
        # result = await composio_client.create_tweet("Test tweet from Composio integration")
        # print(f"✍️ Tweet created: {result.get('id')}")
        
        print("✅ Composio integration test completed")
        
    except Exception as e:
        print(f"❌ Composio test failed: {e}")


async def test_twitter_agent_with_integrations():
    """Test Twitter Agent with Fetch.ai and Composio integrations"""
    print("\n🚀 Testing Twitter Agent with Integrations")
    print("=" * 50)
    
    agent = TwitterAgent()
    
    try:
        # Test natural language processing
        result = await agent.process_natural_language_request(
            "Find 5 tweets about artificial intelligence"
        )
        print(f"🗣️ Natural language request processed: {result['status']}")
        print(f"📊 Tasks executed: {result['tasks_executed']}")
        
        # Test tweet search with Composio
        search_result = await agent.search_tweets("machine learning", max_results=10)
        print(f"🔍 Search completed: {search_result['tweet_count']} tweets found")
        
        # Test trend analysis
        trend_result = await agent.analyze_trends("AI", "24h")
        print(f"📈 Trend analysis completed for topic: {trend_result['topic']}")
        
        # Test user monitoring with Fetch.ai scheduling
        task_id = await agent.monitor_user("elonmusk", ["AI", "Tesla"])
        print(f"👥 User monitoring scheduled: {task_id}")
        
        # Test agent status
        status = await agent.get_agent_status()
        print(f"📊 Agent status: {status}")
        
        # Cleanup
        await agent.cleanup()
        print("🧹 Agent cleanup completed")
        
    except Exception as e:
        print(f"❌ Twitter Agent test failed: {e}")
        await agent.cleanup()


async def test_fallback_behavior():
    """Test fallback behavior when integrations are not available"""
    print("\n🔄 Testing Fallback Behavior")
    print("=" * 50)
    
    # Temporarily disable integrations
    original_fetch_key = os.environ.get("FETCH_AI_API_KEY")
    original_composio_key = os.environ.get("COMPOSIO_API_KEY")
    
    try:
        # Remove API keys to test fallback
        if "FETCH_AI_API_KEY" in os.environ:
            del os.environ["FETCH_AI_API_KEY"]
        if "COMPOSIO_API_KEY" in os.environ:
            del os.environ["COMPOSIO_API_KEY"]
        
        agent = TwitterAgent()
        
        # Test that agent still works with fallbacks
        result = await agent.search_tweets("test query", max_results=5)
        print(f"✅ Fallback search completed: {result['tweet_count']} tweets")
        
        # Test scheduling fallback
        task_id = await agent.monitor_user("testuser", ["test"])
        print(f"✅ Fallback scheduling completed: {task_id}")
        
        await agent.cleanup()
        print("✅ Fallback behavior test completed")
        
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
    finally:
        # Restore original API keys
        if original_fetch_key:
            os.environ["FETCH_AI_API_KEY"] = original_fetch_key
        if original_composio_key:
            os.environ["COMPOSIO_API_KEY"] = original_composio_key


async def main():
    """Run all integration tests"""
    print("🧪 Twitter Agent Integration Tests")
    print("=" * 50)
    
    # Check if API keys are configured
    fetch_key = os.getenv("FETCH_AI_API_KEY")
    composio_key = os.getenv("COMPOSIO_API_KEY")
    twitter_key = os.getenv("TWITTER_BEARER_TOKEN")
    
    print(f"🔑 Fetch.ai API Key: {'✅ Configured' if fetch_key else '❌ Not configured'}")
    print(f"🔑 Composio API Key: {'✅ Configured' if composio_key else '❌ Not configured'}")
    print(f"🔑 Twitter API Key: {'✅ Configured' if twitter_key else '❌ Not configured'}")
    print()
    
    # Run tests
    await test_fetch_ai_integration()
    await test_composio_integration()
    await test_twitter_agent_with_integrations()
    await test_fallback_behavior()
    
    print("\n🎉 All integration tests completed!")
    print("\n📝 Summary:")
    print("- Fetch.ai: Provides autonomous agent scheduling and workflow execution")
    print("- Composio: Provides Twitter API integration with fallback to direct API")
    print("- Fallback: System works even without external integrations")
    print("- Hybrid: Best of both worlds with graceful degradation")


if __name__ == "__main__":
    asyncio.run(main())
