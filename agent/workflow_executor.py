"""
Workflow executor for Twitter Agent tasks
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from agent.twitter_client import TwitterClient
from agent.task_models import AgentTask


class WorkflowExecutor:
    """
    Executes agent tasks by coordinating with Twitter client
    """
    
    def __init__(self, twitter_client: TwitterClient):
        self.twitter_client = twitter_client
        
        # Task handlers mapping
        self.task_handlers = {
            "search_tweets": self._handle_search_tweets,
            "get_user_timeline": self._handle_get_user_timeline,
            "create_tweet": self._handle_create_tweet,
            "like_tweet": self._handle_like_tweet,
            "retweet": self._handle_retweet,
            "follow_user": self._handle_follow_user,
            "get_trends": self._handle_get_trends,
            "analyze_sentiment": self._handle_analyze_sentiment,
            "monitor_user": self._handle_monitor_user,
            "bookmark_tweet": self._handle_bookmark_tweet,
            "create_list": self._handle_create_list,
            "add_to_list": self._handle_add_to_list,
            "get_user_info": self._handle_get_user_info,
            "get_tweet_by_id": self._handle_get_tweet_by_id,
            "get_followers": self._handle_get_followers,
            "get_following": self._handle_get_following
        }

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a single agent task"""
        try:
            logger.info(f"Executing task: {task.type} with params: {task.parameters}")
            
            # Get handler for task type
            handler = self.task_handlers.get(task.type)
            if not handler:
                raise ValueError(f"Unknown task type: {task.type}")
            
            # Execute the task
            result = await handler(task.parameters)
            
            logger.info(f"Task {task.type} completed successfully")
            return {
                "task_id": task.id,
                "type": task.type,
                "status": "success",
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            raise

    async def _handle_search_tweets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tweet search task"""
        query = params.get("query", "")
        max_results = params.get("max_results", 100)
        time_range = params.get("time_range", "24h")
        
        # Calculate time range
        end_time = datetime.utcnow()
        if time_range == "1h":
            start_time = end_time - timedelta(hours=1)
        elif time_range == "24h":
            start_time = end_time - timedelta(hours=24)
        elif time_range == "7d":
            start_time = end_time - timedelta(days=7)
        else:
            start_time = None
        
        tweets = await self.twitter_client.search_recent_tweets(
            query=query,
            max_results=max_results,
            start_time=start_time,
            end_time=end_time
        )
        
        return {
            "query": query,
            "tweet_count": len(tweets),
            "tweets": tweets,
            "time_range": time_range
        }

    async def _handle_get_user_timeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get user timeline task"""
        username = params.get("username", "")
        max_results = params.get("max_results", 100)
        
        # Get user ID first
        user_info = await self.twitter_client.get_user_by_username(username)
        user_id = user_info["id"]
        
        tweets = await self.twitter_client.get_user_timeline(
            user_id=user_id,
            max_results=max_results
        )
        
        return {
            "username": username,
            "user_id": user_id,
            "tweet_count": len(tweets),
            "tweets": tweets
        }

    async def _handle_create_tweet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create tweet task"""
        text = params.get("text", "")
        reply_to = params.get("reply_to_tweet_id")
        media_ids = params.get("media_ids", [])
        
        result = await self.twitter_client.create_tweet(
            text=text,
            reply_to_tweet_id=reply_to,
            media_ids=media_ids
        )
        
        return {
            "tweet_id": result["id"],
            "text": text,
            "created_at": datetime.utcnow().isoformat()
        }

    async def _handle_like_tweet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle like tweet task"""
        tweet_id = params.get("tweet_id", "")
        
        success = await self.twitter_client.like_tweet(tweet_id)
        
        return {
            "tweet_id": tweet_id,
            "liked": success,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_retweet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle retweet task"""
        tweet_id = params.get("tweet_id", "")
        
        success = await self.twitter_client.retweet(tweet_id)
        
        return {
            "tweet_id": tweet_id,
            "retweeted": success,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_follow_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle follow user task"""
        username = params.get("username", "")
        
        # Get user ID first
        user_info = await self.twitter_client.get_user_by_username(username)
        user_id = user_info["id"]
        
        success = await self.twitter_client.follow_user(user_id)
        
        return {
            "username": username,
            "user_id": user_id,
            "followed": success,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_trends(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get trends task"""
        woeid = params.get("woeid", 1)  # Worldwide by default
        
        trends = await self.twitter_client.get_trending_topics(woeid)
        
        return {
            "woeid": woeid,
            "trend_count": len(trends),
            "trends": trends
        }

    async def _handle_analyze_sentiment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sentiment analysis task"""
        tweets = params.get("tweets", [])
        
        # Simple sentiment analysis based on tweet text
        positive_words = ["good", "great", "awesome", "amazing", "love", "best", "excellent"]
        negative_words = ["bad", "terrible", "awful", "hate", "worst", "horrible", "disappointed"]
        
        sentiment_scores = []
        for tweet in tweets:
            text = tweet.get("text", "").lower()
            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)
            
            if positive_count > negative_count:
                sentiment = "positive"
            elif negative_count > positive_count:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            sentiment_scores.append({
                "tweet_id": tweet.get("id"),
                "sentiment": sentiment,
                "positive_words": positive_count,
                "negative_words": negative_count
            })
        
        # Calculate overall sentiment
        total_positive = sum(1 for s in sentiment_scores if s["sentiment"] == "positive")
        total_negative = sum(1 for s in sentiment_scores if s["sentiment"] == "negative")
        total_neutral = sum(1 for s in sentiment_scores if s["sentiment"] == "neutral")
        
        overall_sentiment = "positive" if total_positive > total_negative else "negative" if total_negative > total_positive else "neutral"
        
        return {
            "total_tweets": len(tweets),
            "sentiment_breakdown": {
                "positive": total_positive,
                "negative": total_negative,
                "neutral": total_neutral
            },
            "overall_sentiment": overall_sentiment,
            "detailed_scores": sentiment_scores
        }

    async def _handle_monitor_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user monitoring task"""
        username = params.get("username", "")
        keywords = params.get("keywords", [])
        interval = params.get("interval", 3600)
        
        # Get user info
        user_info = await self.twitter_client.get_user_by_username(username)
        
        # Get recent tweets
        tweets = await self.twitter_client.get_user_timeline(
            user_id=user_info["id"],
            max_results=50
        )
        
        # Filter tweets by keywords if provided
        filtered_tweets = tweets
        if keywords:
            filtered_tweets = [
                tweet for tweet in tweets
                if any(keyword.lower() in tweet.get("text", "").lower() for keyword in keywords)
            ]
        
        return {
            "username": username,
            "user_id": user_info["id"],
            "keywords": keywords,
            "monitoring_interval": interval,
            "recent_tweets": len(tweets),
            "filtered_tweets": len(filtered_tweets),
            "tweets": filtered_tweets
        }

    async def _handle_bookmark_tweet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bookmark tweet task"""
        tweet_id = params.get("tweet_id", "")
        
        # Note: Bookmarking requires additional API implementation
        # For now, return a placeholder response
        logger.info(f"Bookmark tweet {tweet_id} requested")
        
        return {
            "tweet_id": tweet_id,
            "bookmarked": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_create_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create list task"""
        name = params.get("name", "")
        description = params.get("description", "")
        private = params.get("private", False)
        
        # Note: List creation requires additional API implementation
        # For now, return a placeholder response
        logger.info(f"Create list '{name}' requested")
        
        return {
            "list_name": name,
            "description": description,
            "private": private,
            "created": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_add_to_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add to list task"""
        list_id = params.get("list_id", "")
        username = params.get("username", "")
        
        # Note: Add to list requires additional API implementation
        # For now, return a placeholder response
        logger.info(f"Add user {username} to list {list_id} requested")
        
        return {
            "list_id": list_id,
            "username": username,
            "added": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_user_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get user info task"""
        username = params.get("username", "")
        
        user_info = await self.twitter_client.get_user_by_username(username)
        
        return {
            "user_info": user_info,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_tweet_by_id(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get tweet by ID task"""
        tweet_id = params.get("tweet_id", "")
        
        tweet = await self.twitter_client.get_tweet_by_id(tweet_id)
        
        return {
            "tweet": tweet,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_followers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get followers task"""
        username = params.get("username", "")
        max_results = params.get("max_results", 100)
        
        # Get user ID first
        user_info = await self.twitter_client.get_user_by_username(username)
        user_id = user_info["id"]
        
        followers = await self.twitter_client.get_user_followers(
            user_id=user_id,
            max_results=max_results
        )
        
        return {
            "username": username,
            "user_id": user_id,
            "follower_count": len(followers),
            "followers": followers
        }

    async def _handle_get_following(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get following task"""
        username = params.get("username", "")
        max_results = params.get("max_results", 100)
        
        # Get user ID first
        user_info = await self.twitter_client.get_user_by_username(username)
        user_id = user_info["id"]
        
        following = await self.twitter_client.get_user_following(
            user_id=user_id,
            max_results=max_results
        )
        
        return {
            "username": username,
            "user_id": user_id,
            "following_count": len(following),
            "following": following
        }
