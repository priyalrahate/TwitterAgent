"""
Twitter API client using Composio tools and direct API calls
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import httpx
import tweepy

from config.settings import settings
from agent.composio_client import ComposioClient


class TwitterClient:
    """
    Twitter API client that handles all Twitter operations
    Uses Composio for Twitter API integration with fallback to direct API calls
    """
    
    def __init__(self):
        # Initialize Composio client
        self.composio_client = ComposioClient()
        
        # Fallback: Initialize Tweepy client for direct API calls
        self.client = tweepy.Client(
            bearer_token=settings.TWITTER_BEARER_TOKEN,
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        
        # HTTP client for direct API calls
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}",
                "Content-Type": "application/json"
            }
        )
        
        # Rate limiting
        self.rate_limit_delay = settings.RATE_LIMIT_DELAY
        self.last_request_time = 0
        
        # Initialize Composio
        asyncio.create_task(self.composio_client.initialize())
        
        logger.info("Twitter client initialized with Composio integration")

    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = asyncio.get_event_loop().time()

    async def search_recent_tweets(self, query: str, max_results: int = 100,
                                 start_time: Optional[datetime] = None,
                                 end_time: Optional[datetime] = None,
                                 tweet_fields: List[str] = None) -> List[Dict[str, Any]]:
        """Search for recent tweets using Composio with fallback to direct API"""
        try:
            # Try Composio first
            if self.composio_client.is_initialized:
                try:
                    tweets = await self.composio_client.search_tweets(
                        query=query,
                        max_results=max_results,
                        start_time=start_time,
                        end_time=end_time
                    )
                    logger.info(f"Found {len(tweets)} tweets via Composio for query: {query}")
                    return tweets
                except Exception as e:
                    logger.warning(f"Composio search failed, falling back to direct API: {e}")
            
            # Fallback to direct API
            await self._rate_limit()
            
            # Default tweet fields
            if tweet_fields is None:
                tweet_fields = [
                    "id", "text", "created_at", "author_id", "public_metrics",
                    "context_annotations", "entities", "lang", "possibly_sensitive"
                ]
            
            # Format time parameters
            start_time_str = start_time.isoformat() + "Z" if start_time else None
            end_time_str = end_time.isoformat() + "Z" if end_time else None
            
            # Search tweets
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),  # API limit
                start_time=start_time_str,
                end_time=end_time_str,
                tweet_fields=tweet_fields,
                expansions=["author_id"],
                user_fields=["username", "name", "verified", "public_metrics"]
            )
            
            tweets = []
            if response.data:
                # Get user data
                users = {user.id: user for user in response.includes.get('users', [])}
                
                for tweet in response.data:
                    tweet_dict = tweet.data
                    tweet_dict['author_info'] = users.get(tweet.author_id, {})
                    tweets.append(tweet_dict)
            
            logger.info(f"Found {len(tweets)} tweets via direct API for query: {query}")
            return tweets
            
        except Exception as e:
            logger.error(f"Tweet search failed: {e}")
            raise

    async def search_full_archive(self, query: str, max_results: int = 100,
                                start_time: Optional[datetime] = None,
                                end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Search full archive of tweets (requires Academic Research access)"""
        try:
            await self._rate_limit()
            
            # Format time parameters
            start_time_str = start_time.isoformat() + "Z" if start_time else None
            end_time_str = end_time.isoformat() + "Z" if end_time else None
            
            response = self.client.search_all_tweets(
                query=query,
                max_results=min(max_results, 500),  # API limit
                start_time=start_time_str,
                end_time=end_time_str,
                tweet_fields=["id", "text", "created_at", "author_id", "public_metrics"],
                expansions=["author_id"],
                user_fields=["username", "name", "verified"]
            )
            
            tweets = []
            if response.data:
                users = {user.id: user for user in response.includes.get('users', [])}
                
                for tweet in response.data:
                    tweet_dict = tweet.data
                    tweet_dict['author_info'] = users.get(tweet.author_id, {})
                    tweets.append(tweet_dict)
            
            logger.info(f"Found {len(tweets)} archive tweets for query: {query}")
            return tweets
            
        except Exception as e:
            logger.error(f"Full archive search failed: {e}")
            raise

    async def get_user_timeline(self, user_id: str, max_results: int = 100,
                              start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get tweets from a user's timeline using Composio with fallback to direct API"""
        try:
            # Try Composio first
            if self.composio_client.is_initialized:
                try:
                    tweets = await self.composio_client.get_user_timeline(user_id, max_results)
                    logger.info(f"Retrieved {len(tweets)} tweets from user timeline via Composio")
                    return tweets
                except Exception as e:
                    logger.warning(f"Composio get user timeline failed, falling back to direct API: {e}")
            
            # Fallback to direct API
            await self._rate_limit()
            
            start_time_str = start_time.isoformat() + "Z" if start_time else None
            end_time_str = end_time.isoformat() + "Z" if end_time else None
            
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                start_time=start_time_str,
                end_time=end_time_str,
                tweet_fields=["id", "text", "created_at", "public_metrics", "entities"],
                expansions=["author_id"],
                user_fields=["username", "name", "verified"]
            )
            
            tweets = []
            if response.data:
                users = {user.id: user for user in response.includes.get('users', [])}
                
                for tweet in response.data:
                    tweet_dict = tweet.data
                    tweet_dict['author_info'] = users.get(tweet.author_id, {})
                    tweets.append(tweet_dict)
            
            logger.info(f"Retrieved {len(tweets)} tweets from user timeline via direct API")
            return tweets
            
        except Exception as e:
            logger.error(f"User timeline retrieval failed: {e}")
            raise

    async def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """Get user information by username using Composio with fallback to direct API"""
        try:
            # Try Composio first
            if self.composio_client.is_initialized:
                try:
                    user_data = await self.composio_client.get_user_by_username(username)
                    logger.info(f"Retrieved user data for @{username} via Composio")
                    return user_data
                except Exception as e:
                    logger.warning(f"Composio get user by username failed, falling back to direct API: {e}")
            
            # Fallback to direct API
            await self._rate_limit()
            
            response = self.client.get_user(
                username=username,
                user_fields=["id", "username", "name", "description", "verified", 
                           "public_metrics", "created_at", "location", "url"]
            )
            
            if response.data:
                logger.info(f"Retrieved user data for @{username} via direct API")
                return response.data.data
            else:
                raise ValueError(f"User {username} not found")
                
        except Exception as e:
            logger.error(f"User lookup failed: {e}")
            raise

    async def create_tweet(self, text: str, reply_to_tweet_id: str = None,
                         media_ids: List[str] = None) -> Dict[str, Any]:
        """Create a new tweet using Composio with fallback to direct API"""
        try:
            # Try Composio first
            if self.composio_client.is_initialized:
                try:
                    result = await self.composio_client.create_tweet(
                        text=text,
                        reply_to_tweet_id=reply_to_tweet_id,
                        media_ids=media_ids
                    )
                    logger.info(f"Tweet created successfully via Composio: {result.get('id')}")
                    return result
                except Exception as e:
                    logger.warning(f"Composio tweet creation failed, falling back to direct API: {e}")
            
            # Fallback to direct API
            await self._rate_limit()
            
            response = self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=reply_to_tweet_id,
                media_ids=media_ids
            )
            
            if response.data:
                logger.info(f"Tweet created successfully via direct API: {response.data['id']}")
                return response.data
            else:
                raise ValueError("Failed to create tweet")
                
        except Exception as e:
            logger.error(f"Tweet creation failed: {e}")
            raise

    async def like_tweet(self, tweet_id: str) -> bool:
        """Like a tweet using Composio with fallback to direct API"""
        try:
            # Try Composio first
            if self.composio_client.is_initialized:
                try:
                    result = await self.composio_client.like_tweet(tweet_id)
                    logger.info(f"Tweet {tweet_id} liked successfully via Composio")
                    return result
                except Exception as e:
                    logger.warning(f"Composio like tweet failed, falling back to direct API: {e}")
            
            # Fallback to direct API
            await self._rate_limit()
            
            response = self.client.like(tweet_id)
            
            if response.data:
                logger.info(f"Tweet {tweet_id} liked successfully via direct API")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Like tweet failed: {e}")
            raise

    async def retweet(self, tweet_id: str) -> bool:
        """Retweet a tweet using Composio with fallback to direct API"""
        try:
            # Try Composio first
            if self.composio_client.is_initialized:
                try:
                    result = await self.composio_client.retweet(tweet_id)
                    logger.info(f"Tweet {tweet_id} retweeted successfully via Composio")
                    return result
                except Exception as e:
                    logger.warning(f"Composio retweet failed, falling back to direct API: {e}")
            
            # Fallback to direct API
            await self._rate_limit()
            
            response = self.client.retweet(tweet_id)
            
            if response.data:
                logger.info(f"Tweet {tweet_id} retweeted successfully via direct API")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Retweet failed: {e}")
            raise

    async def follow_user(self, user_id: str) -> bool:
        """Follow a user using Composio with fallback to direct API"""
        try:
            # Try Composio first
            if self.composio_client.is_initialized:
                try:
                    result = await self.composio_client.follow_user(user_id)
                    logger.info(f"User {user_id} followed successfully via Composio")
                    return result
                except Exception as e:
                    logger.warning(f"Composio follow user failed, falling back to direct API: {e}")
            
            # Fallback to direct API
            await self._rate_limit()
            
            response = self.client.follow_user(user_id)
            
            if response.data:
                logger.info(f"User {user_id} followed successfully via direct API")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Follow user failed: {e}")
            raise

    async def get_trending_topics(self, woeid: int = 1) -> List[Dict[str, Any]]:
        """Get trending topics using Composio with fallback to direct API"""
        try:
            # Try Composio first
            if self.composio_client.is_initialized:
                try:
                    trends = await self.composio_client.get_trending_topics(woeid)
                    logger.info(f"Retrieved {len(trends)} trending topics via Composio")
                    return trends
                except Exception as e:
                    logger.warning(f"Composio get trending topics failed, falling back to direct API: {e}")
            
            # Fallback to direct API
            await self._rate_limit()
            
            # Use direct API call for trends
            url = f"https://api.twitter.com/1.1/trends/place.json?id={woeid}"
            
            async with self.http_client.get(url) as response:
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        trends = data[0].get('trends', [])
                        logger.info(f"Retrieved {len(trends)} trending topics via direct API")
                        return trends
                    else:
                        return []
                else:
                    raise Exception(f"Trends API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Get trending topics failed: {e}")
            raise

    async def get_tweet_by_id(self, tweet_id: str) -> Dict[str, Any]:
        """Get a specific tweet by ID"""
        try:
            await self._rate_limit()
            
            response = self.client.get_tweet(
                tweet_id,
                tweet_fields=["id", "text", "created_at", "author_id", "public_metrics", "entities"],
                expansions=["author_id"],
                user_fields=["username", "name", "verified"]
            )
            
            if response.data:
                tweet_dict = response.data.data
                if response.includes and 'users' in response.includes:
                    users = {user.id: user for user in response.includes['users']}
                    tweet_dict['author_info'] = users.get(tweet_dict['author_id'], {})
                return tweet_dict
            else:
                raise ValueError(f"Tweet {tweet_id} not found")
                
        except Exception as e:
            logger.error(f"Get tweet by ID failed: {e}")
            raise

    async def get_user_followers(self, user_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get followers of a user"""
        try:
            await self._rate_limit()
            
            response = self.client.get_users_followers(
                id=user_id,
                max_results=min(max_results, 1000),
                user_fields=["id", "username", "name", "verified", "public_metrics"]
            )
            
            followers = []
            if response.data:
                for user in response.data:
                    followers.append(user.data)
            
            logger.info(f"Retrieved {len(followers)} followers")
            return followers
            
        except Exception as e:
            logger.error(f"Get followers failed: {e}")
            raise

    async def get_user_following(self, user_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get users that a user is following"""
        try:
            await self._rate_limit()
            
            response = self.client.get_users_following(
                id=user_id,
                max_results=min(max_results, 1000),
                user_fields=["id", "username", "name", "verified", "public_metrics"]
            )
            
            following = []
            if response.data:
                for user in response.data:
                    following.append(user.data)
            
            logger.info(f"Retrieved {len(following)} following users")
            return following
            
        except Exception as e:
            logger.error(f"Get following failed: {e}")
            raise

    async def upload_media(self, file_path: str, media_type: str = "image") -> str:
        """Upload media file and return media ID"""
        try:
            await self._rate_limit()
            
            # This would require additional implementation for media upload
            # For now, return a placeholder
            logger.info(f"Media upload requested for: {file_path}")
            return "media_id_placeholder"
            
        except Exception as e:
            logger.error(f"Media upload failed: {e}")
            raise

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()
        logger.info("Twitter client closed")
