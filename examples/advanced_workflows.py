"""
Advanced workflow examples for Twitter Agent
"""
import asyncio
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agent.core_agent import TwitterAgent
from workflows.workflow_manager import WorkflowManager


async def custom_trend_monitor():
    """Custom trend monitoring workflow"""
    print("📊 Custom Trend Monitor")
    print("=" * 50)
    
    agent = TwitterAgent()
    workflow_manager = WorkflowManager(agent)
    
    try:
        # Define custom workflow parameters
        parameters = {
            "topics": ["Bitcoin", "Ethereum", "AI", "Web3"],
            "max_tweets_per_topic": 150,
            "timeframe": "24h",
            "sentiment_threshold": 0.6
        }
        
        # Execute trend monitor workflow
        result = await workflow_manager.execute_workflow("trend_monitor", parameters)
        
        print(f"Workflow status: {result['status']}")
        print(f"Steps completed: {len(result['results'])}")
        
        # Process results
        for step_result in result['results']:
            if step_result['status'] == 'success':
                print(f"✅ {step_result['action']}: Completed")
            else:
                print(f"❌ {step_result['action']}: Failed - {step_result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()


async def influencer_monitoring():
    """Monitor multiple influencers"""
    print("\n👥 Influencer Monitoring")
    print("=" * 50)
    
    agent = TwitterAgent()
    workflow_manager = WorkflowManager(agent)
    
    try:
        # Define influencers to monitor
        influencers = [
            {"username": "elonmusk", "keywords": ["AI", "Tesla", "SpaceX"]},
            {"username": "naval", "keywords": ["startup", "entrepreneurship"]},
            {"username": "balajis", "keywords": ["crypto", "Web3"]}
        ]
        
        # Schedule monitoring for each influencer
        task_ids = []
        for influencer in influencers:
            task_id = await workflow_manager.schedule_workflow(
                "user_monitor",
                {
                    "username": influencer["username"],
                    "keywords": influencer["keywords"],
                    "min_engagement": 1000
                },
                {"interval": 1800}  # 30 minutes
            )
            task_ids.append(task_id)
            print(f"✅ Monitoring @{influencer['username']} (Task ID: {task_id})")
        
        print(f"\nTotal monitoring tasks: {len(task_ids)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()


async def content_curation_pipeline():
    """Automated content curation pipeline"""
    print("\n🎯 Content Curation Pipeline")
    print("=" * 50)
    
    agent = TwitterAgent()
    workflow_manager = WorkflowManager(agent)
    
    try:
        # Define content curation parameters
        parameters = {
            "topics": ["AI", "Machine Learning", "Data Science"],
            "sources": ["verified", "influencers"],
            "min_quality_score": 0.8,
            "max_posts_per_day": 3
        }
        
        # Execute content curation workflow
        result = await workflow_manager.execute_workflow("content_curator", parameters)
        
        print(f"Content curation status: {result['status']}")
        
        # Analyze results
        if result['status'] == 'success':
            output = result.get('output', {})
            print(f"Topics curated: {len(parameters['topics'])}")
            print(f"Content found: {output.get('curated_count', 0)}")
            print(f"Posts scheduled: {output.get('scheduled_posts', 0)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()


async def sentiment_analysis_dashboard():
    """Comprehensive sentiment analysis"""
    print("\n😊 Sentiment Analysis Dashboard")
    print("=" * 50)
    
    agent = TwitterAgent()
    workflow_manager = WorkflowManager(agent)
    
    try:
        # Define analysis parameters
        topics = ["Bitcoin", "Ethereum", "AI", "Web3", "DeFi"]
        
        sentiment_results = {}
        
        for topic in topics:
            print(f"Analyzing sentiment for: {topic}")
            
            result = await workflow_manager.execute_workflow(
                "sentiment_analyzer",
                {
                    "topic": topic,
                    "timeframe": "24h",
                    "max_tweets": 200,
                    "sentiment_threshold": 0.6
                }
            )
            
            if result['status'] == 'success':
                output = result.get('output', {})
                sentiment_results[topic] = {
                    "total_tweets": output.get('total_tweets', 0),
                    "sentiment_distribution": output.get('sentiment_distribution', {}),
                    "key_themes": output.get('key_themes', []),
                    "insights": output.get('insights', [])
                }
                print(f"  ✅ {topic}: {output.get('total_tweets', 0)} tweets analyzed")
            else:
                print(f"  ❌ {topic}: Analysis failed")
        
        # Generate summary report
        print("\n📊 Sentiment Analysis Summary:")
        print("-" * 30)
        for topic, data in sentiment_results.items():
            sentiment = data['sentiment_distribution']
            print(f"{topic}:")
            print(f"  Total tweets: {data['total_tweets']}")
            print(f"  Positive: {sentiment.get('positive', 0)}")
            print(f"  Neutral: {sentiment.get('neutral', 0)}")
            print(f"  Negative: {sentiment.get('negative', 0)}")
            print()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()


async def engagement_optimization():
    """Engagement optimization workflow"""
    print("\n🚀 Engagement Optimization")
    print("=" * 50)
    
    agent = TwitterAgent()
    workflow_manager = WorkflowManager(agent)
    
    try:
        # Define optimization parameters
        parameters = {
            "username": "your_username",  # Replace with actual username
            "min_engagement_threshold": 50,
            "boost_delay": 300,
            "max_boosts_per_day": 5
        }
        
        # Execute engagement booster workflow
        result = await workflow_manager.execute_workflow("engagement_booster", parameters)
        
        print(f"Engagement optimization status: {result['status']}")
        
        if result['status'] == 'success':
            output = result.get('output', {})
            print(f"Tweets checked: {output.get('tweets_checked', 0)}")
            print(f"Low engagement tweets: {output.get('low_engagement_count', 0)}")
            print(f"Boosts scheduled: {output.get('boosts_scheduled', 0)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()


async def real_time_monitoring():
    """Real-time monitoring setup"""
    print("\n⏰ Real-time Monitoring")
    print("=" * 50)
    
    agent = TwitterAgent()
    workflow_manager = WorkflowManager(agent)
    
    try:
        # Set up multiple monitoring tasks
        monitoring_tasks = [
            {
                "name": "Crypto Trends",
                "workflow": "trend_monitor",
                "parameters": {"topics": ["Bitcoin", "Ethereum"], "max_tweets": 100},
                "schedule": {"interval": 900}  # 15 minutes
            },
            {
                "name": "AI News",
                "workflow": "trend_monitor",
                "parameters": {"topics": ["AI", "Machine Learning"], "max_tweets": 100},
                "schedule": {"interval": 1800}  # 30 minutes
            },
            {
                "name": "Tech Influencers",
                "workflow": "user_monitor",
                "parameters": {"username": "elonmusk", "keywords": ["AI", "Tesla"]},
                "schedule": {"interval": 3600}  # 1 hour
            }
        ]
        
        scheduled_tasks = []
        for task in monitoring_tasks:
            task_id = await workflow_manager.schedule_workflow(
                task["workflow"],
                task["parameters"],
                task["schedule"]
            )
            scheduled_tasks.append({
                "name": task["name"],
                "task_id": task_id
            })
            print(f"✅ {task['name']}: Scheduled (ID: {task_id})")
        
        print(f"\nTotal monitoring tasks: {len(scheduled_tasks)}")
        
        # Get agent status
        status = await agent.get_agent_status()
        print(f"Active tasks: {status['active_tasks']}")
        print(f"Scheduled workflows: {status['scheduled_workflows']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()


async def workflow_management():
    """Workflow management operations"""
    print("\n⚙️ Workflow Management")
    print("=" * 50)
    
    agent = TwitterAgent()
    workflow_manager = WorkflowManager(agent)
    
    try:
        # List all available workflows
        workflows = workflow_manager.list_workflows()
        print("Available workflows:")
        for workflow in workflows:
            print(f"  - {workflow['name']}: {workflow['description']}")
        
        # Get scheduled tasks
        scheduled_tasks = await agent.scheduler.get_scheduled_tasks()
        print(f"\nScheduled tasks: {len(scheduled_tasks)}")
        
        for task in scheduled_tasks:
            print(f"  - {task['name']}: {task['status']} (Next run: {task['next_run']})")
        
        # Example: Cancel a task (if any exist)
        if scheduled_tasks:
            task_to_cancel = scheduled_tasks[0]
            success = await workflow_manager.cancel_workflow(task_to_cancel['id'])
            if success:
                print(f"✅ Cancelled task: {task_to_cancel['name']}")
            else:
                print(f"❌ Failed to cancel task: {task_to_cancel['name']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()


async def main():
    """Run all advanced examples"""
    print("🚀 Advanced Twitter Agent Workflows")
    print("=" * 50)
    
    # Run examples
    await custom_trend_monitor()
    await influencer_monitoring()
    await content_curation_pipeline()
    await sentiment_analysis_dashboard()
    await engagement_optimization()
    await real_time_monitoring()
    await workflow_management()
    
    print("\n✅ All advanced examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
