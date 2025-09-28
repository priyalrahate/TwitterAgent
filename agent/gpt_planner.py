"""
GPT-based task planner and analyzer for Twitter Agent
"""
import json
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

import openai
from config.settings import settings


class GPTPlanner:
    """
    GPT-powered planner that:
    1. Converts natural language requests into structured task plans
    2. Analyzes tweet data and generates insights
    3. Creates responses for user queries
    """
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.GPT_MODEL
        self.temperature = settings.GPT_TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
        
        # System prompts for different tasks
        self.task_planning_prompt = """
You are a Twitter Agent Task Planner. Your job is to convert natural language requests into structured task plans.

Available Twitter operations:
- search_tweets: Search for tweets with query, filters, and time ranges
- get_user_timeline: Get tweets from a specific user
- create_tweet: Post a new tweet
- like_tweet: Like a specific tweet
- retweet: Retweet a specific tweet
- follow_user: Follow a user
- get_trends: Get trending topics
- analyze_sentiment: Analyze sentiment of tweets
- monitor_user: Set up monitoring for a user
- bookmark_tweet: Bookmark a tweet
- create_list: Create a Twitter list
- add_to_list: Add user to a list

For each request, create a JSON response with this structure:
{
    "intent": "description of what the user wants",
    "steps": [
        {
            "action": "operation_name",
            "parameters": {
                "param1": "value1",
                "param2": "value2"
            },
            "description": "what this step does"
        }
    ],
    "expected_output": "description of expected result"
}

Examples:
Request: "Find the latest 50 tweets about Bitcoin and analyze sentiment"
Response:
{
    "intent": "Search for Bitcoin tweets and analyze sentiment",
    "steps": [
        {
            "action": "search_tweets",
            "parameters": {
                "query": "Bitcoin",
                "max_results": 50,
                "time_range": "24h"
            },
            "description": "Search for recent Bitcoin tweets"
        },
        {
            "action": "analyze_sentiment",
            "parameters": {
                "tweets": "{{previous_step_result}}"
            },
            "description": "Analyze sentiment of found tweets"
        }
    ],
    "expected_output": "List of Bitcoin tweets with sentiment analysis"
}
"""

        self.tweet_analysis_prompt = """
You are a Twitter Data Analyst. Analyze the provided tweet data and extract insights.

For the given tweets, provide analysis in this JSON format:
{
    "summary": "Brief summary of the tweet collection",
    "sentiment": {
        "positive": 0,
        "neutral": 0,
        "negative": 0,
        "overall": "positive/neutral/negative"
    },
    "top_hashtags": ["#tag1", "#tag2"],
    "top_mentions": ["@user1", "@user2"],
    "engagement_metrics": {
        "avg_likes": 0,
        "avg_retweets": 0,
        "avg_replies": 0
    },
    "key_themes": ["theme1", "theme2"],
    "influential_accounts": ["@user1", "@user2"],
    "insights": [
        "insight 1",
        "insight 2"
    ]
}
"""

        self.trend_analysis_prompt = """
You are a Twitter Trend Analyst. Analyze tweet data to identify trends and patterns.

Provide trend analysis in this JSON format:
{
    "trend_summary": "Overall trend description",
    "trend_direction": "rising/falling/stable",
    "peak_times": ["hour1", "hour2"],
    "geographic_distribution": {
        "top_locations": ["location1", "location2"]
    },
    "content_themes": ["theme1", "theme2"],
    "influencer_activity": {
        "most_active": ["@user1", "@user2"],
        "most_engaging": ["@user1", "@user2"]
    },
    "predictions": [
        "prediction 1",
        "prediction 2"
    ],
    "recommendations": [
        "recommendation 1",
        "recommendation 2"
    ]
}
"""

    async def plan_task(self, request: str) -> Dict[str, Any]:
        """Convert natural language request into structured task plan"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.task_planning_prompt},
                    {"role": "user", "content": f"Request: {request}"}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"GPT planning response: {content}")
            
            # Parse JSON response
            plan = json.loads(content)
            return plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT response as JSON: {e}")
            # Fallback to simple plan
            return {
                "intent": "Process request",
                "steps": [{
                    "action": "search_tweets",
                    "parameters": {"query": request},
                    "description": "Search for tweets related to request"
                }],
                "expected_output": "Search results"
            }
        except Exception as e:
            logger.error(f"Task planning failed: {e}")
            raise

    async def analyze_tweets(self, tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a collection of tweets using GPT"""
        try:
            # Prepare tweet data for analysis
            tweet_data = []
            for tweet in tweets[:50]:  # Limit to 50 tweets for analysis
                tweet_data.append({
                    "text": tweet.get("text", ""),
                    "author": tweet.get("author_id", ""),
                    "created_at": tweet.get("created_at", ""),
                    "public_metrics": tweet.get("public_metrics", {}),
                    "entities": tweet.get("entities", {})
                })
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.tweet_analysis_prompt},
                    {"role": "user", "content": f"Analyze these tweets: {json.dumps(tweet_data, indent=2)}"}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"Tweet analysis response: {content}")
            
            # Parse JSON response
            analysis = json.loads(content)
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis response as JSON: {e}")
            return {
                "summary": "Analysis failed",
                "sentiment": {"overall": "unknown"},
                "insights": ["Unable to analyze tweets"]
            }
        except Exception as e:
            logger.error(f"Tweet analysis failed: {e}")
            raise

    async def analyze_trends(self, tweets: List[Dict[str, Any]], topic: str, timeframe: str) -> Dict[str, Any]:
        """Analyze trends from tweet data"""
        try:
            # Prepare trend data
            trend_data = {
                "topic": topic,
                "timeframe": timeframe,
                "tweet_count": len(tweets),
                "tweets": tweets[:100]  # Limit for analysis
            }
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.trend_analysis_prompt},
                    {"role": "user", "content": f"Analyze trends: {json.dumps(trend_data, indent=2)}"}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"Trend analysis response: {content}")
            
            # Parse JSON response
            trends = json.loads(content)
            return trends
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse trend response as JSON: {e}")
            return {
                "trend_summary": "Trend analysis failed",
                "trend_direction": "unknown",
                "recommendations": ["Unable to analyze trends"]
            }
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            raise

    async def generate_response(self, original_request: str, task_results: List[Dict[str, Any]]) -> str:
        """Generate a natural language response based on task results"""
        try:
            response_prompt = f"""
You are a helpful Twitter Agent assistant. Generate a natural, conversational response to the user's request based on the task results.

Original request: {original_request}

Task results: {json.dumps(task_results, indent=2)}

Provide a clear, informative response that summarizes what was accomplished and highlights key findings.
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful Twitter Agent assistant."},
                    {"role": "user", "content": response_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            return content
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return f"I processed your request '{original_request}' and completed {len(task_results)} tasks. Check the results for details."

    async def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text using GPT"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract the most relevant keywords from the given text. Return as a JSON array of strings."},
                    {"role": "user", "content": f"Text: {text}"}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            keywords = json.loads(content)
            return keywords
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []

    async def generate_tweet_content(self, topic: str, style: str = "informative") -> str:
        """Generate tweet content for a given topic"""
        try:
            style_prompts = {
                "informative": "Write an informative tweet about",
                "engaging": "Write an engaging tweet that encourages interaction about",
                "news": "Write a news-style tweet about",
                "opinion": "Write an opinion tweet about",
                "question": "Write a question tweet about"
            }
            
            prompt = f"{style_prompts.get(style, 'Write a tweet about')} {topic}. Keep it under 280 characters."
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Twitter content creator. Write engaging, concise tweets."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=100
            )
            
            content = response.choices[0].message.content.strip()
            return content
            
        except Exception as e:
            logger.error(f"Tweet content generation failed: {e}")
            return f"Interesting insights about {topic} #AI #Twitter"
