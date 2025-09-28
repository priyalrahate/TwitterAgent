"""
Basic usage examples for Twitter Agent
"""
import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agent.core_agent import TwitterAgent
from workflows.workflow_manager import WorkflowManager


async def basic_search_example():
    """Basic tweet search example"""
    print("🔍 Basic Search Example")
    print("=" * 50)
    
    agent = TwitterAgent()
    
    try:
        # Search for tweets about AI
        result = await agent.search_tweets(
            query="artificial intelligence",
            max_results=50,
            start_time=datetime.utcnow() - timedelta(hours=24)
        )
        
        print(f"Found {result['tweet_count']} tweets")
        print(f"Analysis: {result['analysis']['summary']}")
        print(f"Sentiment: {result['analysis']['sentiment']['overall']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()


async def natural_language_example():
    """Natural language processing example"""
    print("\n🗣️ Natural Language Example")
    print("=" * 50)
    
    agent = TwitterAgent()
    
    try:
        # Process natural language request
        result = await agent.process_natural_language_request(
            "Find the latest 30 tweets about Bitcoin and analyze sentiment"
        )
        
        print(f"Status: {result['status']}")
        print(f"Tasks executed: {result['tasks_executed']}")
        print(f"Response: {result['response']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()


async def trend_analysis_example():
    """Trend analysis example"""
    print("\n📈 Trend Analysis Example")
    print("=" * 50)
    
    agent = TwitterAgent()
    
    try:
        # Analyze trends for Ethereum
        result = await agent.analyze_trends("Ethereum", "7d")
        
        print(f"Topic: {result['topic']}")
        print(f"Timeframe: {result['timeframe']}")
        print(f"Tweet count: {result['tweet_count']}")
        print(f"Trend summary: {result['trend_analysis']['trend_summary']}")
        print(f"Trend direction: {result['trend_analysis']['trend_direction']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()


async def user_monitoring_example():
    """User monitoring example"""
    print("\n👤 User Monitoring Example")
    print("=" * 50)
    
    agent = TwitterAgent()
    
    try:
        # Set up monitoring for a user
        task_id = await agent.monitor_user(
            username="elonmusk",
            keywords=["AI", "Tesla", "SpaceX"],
            schedule_interval=1800  # 30 minutes
        )
        
        print(f"Monitoring started with task ID: {task_id}")
        
        # Get agent status
        status = await agent.get_agent_status()
        print(f"Active tasks: {status['active_tasks']}")
        print(f"Scheduled workflows: {status['scheduled_workflows']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()


async def workflow_example():
    """Workflow execution example"""
    print("\n⚙️ Workflow Example")
    print("=" * 50)
    
    agent = TwitterAgent()
    workflow_manager = WorkflowManager(agent)
    
    try:
        # List available workflows
        workflows = workflow_manager.list_workflows()
        print("Available workflows:")
        for workflow in workflows:
            print(f"  - {workflow['name']}: {workflow['description']}")
        
        # Execute a workflow
        if workflows:
            workflow_name = workflows[0]['name']
            result = await workflow_manager.execute_workflow(
                workflow_name,
                {"topics": ["AI", "Machine Learning"], "max_tweets": 100}
            )
            
            print(f"\nExecuted workflow: {workflow_name}")
            print(f"Status: {result['status']}")
            print(f"Results: {len(result['results'])} steps completed")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()


async def content_creation_example():
    """Content creation example"""
    print("\n✍️ Content Creation Example")
    print("=" * 50)
    
    agent = TwitterAgent()
    
    try:
        # Generate tweet content using GPT
        content = await agent.gpt_planner.generate_tweet_content(
            "artificial intelligence trends",
            style="informative"
        )
        
        print(f"Generated content: {content}")
        
        # Create a post (commented out to avoid actual posting)
        # post_id = await agent.create_automated_post(content)
        # print(f"Post created with ID: {post_id}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()


async def main():
    """Run all examples"""
    print("🚀 Twitter Agent Examples")
    print("=" * 50)
    
    # Check if API keys are configured
    required_keys = [
        "OPENAI_API_KEY",
        "TWITTER_BEARER_TOKEN",
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET"
    ]
    
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        print(f"❌ Missing required environment variables: {', '.join(missing_keys)}")
        print("Please configure your .env file with the required API keys.")
        return
    
    # Run examples
    await basic_search_example()
    await natural_language_example()
    await trend_analysis_example()
    await user_monitoring_example()
    await workflow_example()
    await content_creation_example()
    
    print("\n✅ All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
