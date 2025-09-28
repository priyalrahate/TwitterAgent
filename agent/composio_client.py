"""
Composio integration for Twitter Agent
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

try:
    from composio_core import ComposioToolSet, Action, ActionType
    from composio_openai import ComposioOpenAI
    COMPOSIO_AVAILABLE = True
except ImportError:
    COMPOSIO_AVAILABLE = False
    logger.warning("Composio not available, using mock implementation")

from config.settings import settings


class ComposioClient:
    """
    Composio client for Twitter API operations
    """
    
    def __init__(self):
        self.api_key = settings.COMPOSIO_API_KEY
        self.toolset = None
        self.openai_client = None
        self.is_initialized = False
        
        logger.info("Composio client initialized")

    async def initialize(self):
        """Initialize Composio client"""
        try:
            if not COMPOSIO_AVAILABLE:
                logger.warning("Composio not available, using mock mode")
                return await self._initialize_mock()
            
            if not self.api_key:
                logger.warning("Composio API key not configured, using mock mode")
                return await self._initialize_mock()
            
            # Initialize Composio toolset
            self.toolset = ComposioToolSet(api_key=self.api_key)
            
            # Initialize OpenAI client with Composio
            self.openai_client = ComposioOpenAI(
                api_key=settings.OPENAI_API_KEY,
                composio_api_key=self.api_key
            )
            
            # Register Twitter tools
            await self._register_twitter_tools()
            
            self.is_initialized = True
            logger.info("Composio client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Composio client: {e}")
            return await self._initialize_mock()

    async def _initialize_mock(self):
        """Initialize mock Composio client"""
        self.toolset = MockComposioToolSet()
        self.openai_client = MockComposioOpenAI()
        self.is_initialized = True
        logger.info("Composio mock client initialized")

    async def _register_twitter_tools(self):
        """Register Twitter tools with Composio"""
        try:
            # Get available Twitter actions
            twitter_actions = self.toolset.get_actions(integration="twitter")
            logger.info(f"Registered {len(twitter_actions)} Twitter actions")
        except Exception as e:
            logger.error(f"Failed to register Twitter tools: {e}")

    async def search_tweets(self, query: str, max_results: int = 100, 
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Search tweets using Composio"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Prepare parameters
            params = {
                "query": query,
                "max_results": min(max_results, 100),
                "tweet_fields": ["id", "text", "created_at", "author_id", "public_metrics", "entities"]
            }
            
            if start_time:
                params["start_time"] = start_time.isoformat() + "Z"
            if end_time:
                params["end_time"] = end_time.isoformat() + "Z"
            
            # Execute via Composio
            result = await self.toolset.execute_action(
                action=Action.TWITTER_SEARCH_RECENT_TWEETS,
                params=params
            )
            
            tweets = result.get("data", [])
            logger.info(f"Found {len(tweets)} tweets via Composio")
            return tweets
            
        except Exception as e:
            logger.error(f"Composio tweet search failed: {e}")
            raise

    async def create_tweet(self, text: str, reply_to_tweet_id: str = None,
                         media_ids: List[str] = None) -> Dict[str, Any]:
        """Create tweet using Composio"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            params = {"text": text}
            if reply_to_tweet_id:
                params["in_reply_to_tweet_id"] = reply_to_tweet_id
            if media_ids:
                params["media_ids"] = media_ids
            
            result = await self.toolset.execute_action(
                action=Action.TWITTER_CREATE_TWEET,
                params=params
            )
            
            logger.info(f"Tweet created via Composio: {result.get('id')}")
            return result
            
        except Exception as e:
            logger.error(f"Composio tweet creation failed: {e}")
            raise

    async def like_tweet(self, tweet_id: str) -> bool:
        """Like tweet using Composio"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.toolset.execute_action(
                action=Action.TWITTER_LIKE_TWEET,
                params={"tweet_id": tweet_id}
            )
            
            success = result.get("data", {}).get("liked", False)
            logger.info(f"Tweet {tweet_id} liked via Composio: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Composio like tweet failed: {e}")
            raise

    async def retweet(self, tweet_id: str) -> bool:
        """Retweet using Composio"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.toolset.execute_action(
                action=Action.TWITTER_RETWEET,
                params={"tweet_id": tweet_id}
            )
            
            success = result.get("data", {}).get("retweeted", False)
            logger.info(f"Tweet {tweet_id} retweeted via Composio: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Composio retweet failed: {e}")
            raise

    async def follow_user(self, user_id: str) -> bool:
        """Follow user using Composio"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.toolset.execute_action(
                action=Action.TWITTER_FOLLOW_USER,
                params={"user_id": user_id}
            )
            
            success = result.get("data", {}).get("following", False)
            logger.info(f"User {user_id} followed via Composio: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Composio follow user failed: {e}")
            raise

    async def get_user_timeline(self, user_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get user timeline using Composio"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.toolset.execute_action(
                action=Action.TWITTER_GET_USER_TWEETS,
                params={
                    "user_id": user_id,
                    "max_results": min(max_results, 100),
                    "tweet_fields": ["id", "text", "created_at", "public_metrics", "entities"]
                }
            )
            
            tweets = result.get("data", [])
            logger.info(f"Retrieved {len(tweets)} tweets from user timeline via Composio")
            return tweets
            
        except Exception as e:
            logger.error(f"Composio get user timeline failed: {e}")
            raise

    async def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """Get user by username using Composio"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.toolset.execute_action(
                action=Action.TWITTER_GET_USER_BY_USERNAME,
                params={
                    "username": username,
                    "user_fields": ["id", "username", "name", "description", "verified", "public_metrics"]
                }
            )
            
            user_data = result.get("data", {})
            logger.info(f"Retrieved user data for @{username} via Composio")
            return user_data
            
        except Exception as e:
            logger.error(f"Composio get user by username failed: {e}")
            raise

    async def get_trending_topics(self, woeid: int = 1) -> List[Dict[str, Any]]:
        """Get trending topics using Composio"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.toolset.execute_action(
                action=Action.TWITTER_GET_TRENDS,
                params={"woeid": woeid}
            )
            
            trends = result.get("data", [])
            logger.info(f"Retrieved {len(trends)} trending topics via Composio")
            return trends
            
        except Exception as e:
            logger.error(f"Composio get trending topics failed: {e}")
            raise

    async def bookmark_tweet(self, tweet_id: str) -> bool:
        """Bookmark tweet using Composio"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.toolset.execute_action(
                action=Action.TWITTER_BOOKMARK_TWEET,
                params={"tweet_id": tweet_id}
            )
            
            success = result.get("data", {}).get("bookmarked", False)
            logger.info(f"Tweet {tweet_id} bookmarked via Composio: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Composio bookmark tweet failed: {e}")
            raise

    async def create_list(self, name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """Create Twitter list using Composio"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.toolset.execute_action(
                action=Action.TWITTER_CREATE_LIST,
                params={
                    "name": name,
                    "description": description,
                    "private": private
                }
            )
            
            list_data = result.get("data", {})
            logger.info(f"List '{name}' created via Composio: {list_data.get('id')}")
            return list_data
            
        except Exception as e:
            logger.error(f"Composio create list failed: {e}")
            raise

    async def add_to_list(self, list_id: str, user_id: str) -> bool:
        """Add user to list using Composio"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.toolset.execute_action(
                action=Action.TWITTER_ADD_TO_LIST,
                params={
                    "list_id": list_id,
                    "user_id": user_id
                }
            )
            
            success = result.get("data", {}).get("is_member", False)
            logger.info(f"User {user_id} added to list {list_id} via Composio: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Composio add to list failed: {e}")
            raise


class MockComposioToolSet:
    """Mock Composio toolset for development/testing"""
    
    async def execute_action(self, action, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock action execution"""
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        if "SEARCH_RECENT_TWEETS" in str(action):
            return {
                "data": [
                    {
                        "id": "mock_tweet_1",
                        "text": f"Mock tweet for query: {params.get('query', '')}",
                        "created_at": datetime.utcnow().isoformat(),
                        "author_id": "mock_user_1",
                        "public_metrics": {"like_count": 10, "retweet_count": 5}
                    }
                ]
            }
        elif "CREATE_TWEET" in str(action):
            return {
                "data": {
                    "id": f"mock_tweet_{datetime.utcnow().timestamp()}",
                    "text": params.get("text", ""),
                    "created_at": datetime.utcnow().isoformat()
                }
            }
        elif "LIKE_TWEET" in str(action):
            return {"data": {"liked": True}}
        elif "RETWEET" in str(action):
            return {"data": {"retweeted": True}}
        elif "FOLLOW_USER" in str(action):
            return {"data": {"following": True}}
        elif "GET_USER_TWEETS" in str(action):
            return {
                "data": [
                    {
                        "id": "mock_user_tweet_1",
                        "text": "Mock user tweet",
                        "created_at": datetime.utcnow().isoformat(),
                        "public_metrics": {"like_count": 20, "retweet_count": 10}
                    }
                ]
            }
        elif "GET_USER_BY_USERNAME" in str(action):
            return {
                "data": {
                    "id": "mock_user_1",
                    "username": params.get("username", "mock_user"),
                    "name": "Mock User",
                    "verified": True,
                    "public_metrics": {"followers_count": 1000}
                }
            }
        elif "GET_TRENDS" in str(action):
            return {
                "data": [
                    {"name": "#AI", "tweet_volume": 10000},
                    {"name": "#Web3", "tweet_volume": 8000}
                ]
            }
        elif "BOOKMARK_TWEET" in str(action):
            return {"data": {"bookmarked": True}}
        elif "CREATE_LIST" in str(action):
            return {
                "data": {
                    "id": f"mock_list_{datetime.utcnow().timestamp()}",
                    "name": params.get("name", ""),
                    "description": params.get("description", "")
                }
            }
        elif "ADD_TO_LIST" in str(action):
            return {"data": {"is_member": True}}
        else:
            return {"data": {}}


class MockComposioOpenAI:
    """Mock Composio OpenAI client"""
    
    def __init__(self):
        pass
    
    async def chat_completions_create(self, **kwargs):
        """Mock chat completions"""
        return {
            "choices": [{
                "message": {
                    "content": "Mock response from Composio OpenAI"
                }
            }]
        }
