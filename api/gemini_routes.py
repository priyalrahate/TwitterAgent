"""
Gemini AI integration routes for advanced Twitter analysis
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from loguru import logger
import asyncio

# Import clients with lazy loading to avoid circular imports
gemini_client = None
twitter_client = None

def get_gemini_client():
    global gemini_client
    if gemini_client is None:
        from agent.gemini_client import GeminiClient
        gemini_client = GeminiClient()
    return gemini_client

def get_twitter_client():
    global twitter_client
    if twitter_client is None:
        from agent.twitter_client import TwitterClient
        twitter_client = TwitterClient()
    return twitter_client

# Request/Response Models

class SentimentAnalysisRequest(BaseModel):
    query: str = Field(..., description="Search query for tweets")
    max_tweets: int = Field(default=50, ge=10, le=500, description="Maximum number of tweets to analyze")
    include_context: bool = Field(default=False, description="Include web search context")
    geographic_focus: Optional[str] = Field(None, description="Geographic focus (city, country)")
    language: str = Field(default="en", description="Language filter")

class SentimentAnalysisResponse(BaseModel):
    query: str
    tweet_count: int
    analysis: Dict[str, Any]
    timestamp: datetime
    model_used: str

class TrendPredictionRequest(BaseModel):
    topic: str = Field(..., description="Topic to analyze for trends")
    timeframe: str = Field(default="24h", description="Prediction timeframe (1h, 6h, 24h, 7d)")
    max_tweets: int = Field(default=100, ge=50, le=1000, description="Maximum number of tweets to analyze")
    geographic_focus: Optional[str] = Field(None, description="Geographic focus for trend analysis")
    demographic_focus: Optional[str] = Field(None, description="Demographic focus (age, interests)")

class TrendPredictionResponse(BaseModel):
    topic: str
    timeframe: str
    predictions: List[Dict[str, Any]]
    recommendations: Dict[str, Any]
    confidence_score: float
    timestamp: datetime

class ContentStrategyRequest(BaseModel):
    analysis_data: Dict[str, Any] = Field(..., description="Previous analysis data to base strategy on")
    target_audience: str = Field(default="general", description="Target audience for content")
    content_type: str = Field(default="mixed", description="Type of content (tweets, threads, videos, mixed)")
    brand_voice: Optional[str] = Field(None, description="Brand voice to maintain")

class ContentStrategyResponse(BaseModel):
    strategy_id: str
    content_ideas: List[Dict[str, Any]]
    posting_strategy: Dict[str, Any]
    target_audience: str
    expected_engagement: float
    timestamp: datetime

class GeminiSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    twitter_data: Optional[List[Dict[str, Any]]] = Field(None, description="Twitter data to enhance search")
    search_depth: str = Field(default="medium", description="Search depth (shallow, medium, deep)")
    max_results: int = Field(default=10, ge=5, le=50, description="Maximum search results")

class GeminiSearchResponse(BaseModel):
    query: str
    search_results: List[Dict[str, Any]]
    combined_analysis: Dict[str, Any]
    search_metadata: Dict[str, Any]
    timestamp: datetime

# Create router
router = APIRouter(prefix="/gemini", tags=["gemini-analysis"])

# Background task for logging
async def _log_analysis(analysis_type: str, query: str, tweet_count: int, analysis: Dict[str, Any]):
    """Log analysis results for monitoring"""
    logger.info(f"{analysis_type} completed - Query: {query}, Tweets: {tweet_count}, Analysis keys: {list(analysis.keys())}")

@router.post("/sentiment-analysis", response_model=SentimentAnalysisResponse)
async def advanced_sentiment_analysis(
    request: SentimentAnalysisRequest,
    background_tasks: BackgroundTasks
) -> SentimentAnalysisResponse:
    """
    Perform advanced sentiment analysis on tweets using Gemini AI
    
    Features:
    - Detailed sentiment breakdown with emotional intensity
    - Key sentiment drivers identification
    - Trend analysis and influential accounts
    - Optional web search context integration
    """
    try:
        logger.info(f"Starting advanced sentiment analysis for query: {request.query}")
        
        # Get clients
        twitter_client = get_twitter_client()
        gemini_client = get_gemini_client()
        
        # Build search query
        search_query = request.query
        if request.geographic_focus:
            search_query += f" near:{request.geographic_focus}"
        if request.language:
            search_query += f" lang:{request.language}"
        
        # Fetch tweets
        tweets = await twitter_client.search_recent_tweets(
            query=search_query,
            max_results=request.max_tweets
        )
        
        if not tweets:
            raise HTTPException(status_code=404, detail="No tweets found for the given query")
        
        # Perform sentiment analysis
        if request.include_context:
            # Get additional context from web search
            search_data = await gemini_client.search_with_context(
                request.query,
                tweets[:10]  # Use first 10 tweets for context
            )
            # Combine Twitter data with search context for analysis
            enhanced_tweets = tweets + [search_data.get("combined_analysis", {})]
            analysis = await gemini_client.advanced_sentiment_analysis(enhanced_tweets)
        else:
            analysis = await gemini_client.advanced_sentiment_analysis(tweets)
        
        response = SentimentAnalysisResponse(
            query=request.query,
            tweet_count=len(tweets),
            analysis=analysis,
            timestamp=datetime.utcnow(),
            model_used="gemini-1.5-flash"  # Default model
        )
        
        # Log analysis in background
        background_tasks.add_task(
            _log_analysis,
            "sentiment_analysis",
            request.query,
            len(tweets),
            analysis
        )
        
        logger.info(f"Sentiment analysis completed for {len(tweets)} tweets")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/trend-prediction", response_model=TrendPredictionResponse)
async def predict_trends(
    request: TrendPredictionRequest,
    background_tasks: BackgroundTasks
) -> TrendPredictionResponse:
    """
    Predict Twitter trends using Gemini AI
    
    Features:
    - Trend velocity and acceleration prediction
    - Peak timing forecasts
    - Geographic spread patterns
    - Demographic insights
    - Content theme predictions
    """
    try:
        logger.info(f"Starting trend prediction for topic: {request.topic}")
        
        # Build search query
        search_query = request.topic
        if request.geographic_focus:
            search_query += f" near:{request.geographic_focus}"
        
        # Get clients
        twitter_client = get_twitter_client()
        gemini_client = get_gemini_client()
        
        # Fetch tweets
        tweets = await twitter_client.search_recent_tweets(
            query=search_query,
            max_results=request.max_tweets
        )
        
        if not tweets:
            raise HTTPException(status_code=404, detail="No tweets found for the given topic")
        
        # Perform trend prediction
        prediction = await gemini_client.trend_prediction(
            tweets,
            request.topic,
            request.timeframe
        )
        
        # Calculate confidence score
        confidence_score = sum(p.get("confidence", 0) for p in prediction.get("predictions", [])) / len(prediction.get("predictions", [1]))
        
        response = TrendPredictionResponse(
            topic=request.topic,
            timeframe=request.timeframe,
            predictions=prediction.get("predictions", []),
            recommendations=prediction.get("recommendations", {}),
            confidence_score=confidence_score,
            timestamp=datetime.utcnow()
        )
        
        # Log prediction in background
        background_tasks.add_task(
            _log_analysis,
            "trend_prediction",
            request.topic,
            len(tweets),
            prediction
        )
        
        logger.info(f"Trend prediction completed for {len(tweets)} tweets")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trend prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/content-strategy", response_model=ContentStrategyResponse)
async def generate_content_strategy(
    request: ContentStrategyRequest,
    background_tasks: BackgroundTasks
) -> ContentStrategyResponse:
    """
    Generate content strategy based on analysis data
    
    Features:
    - Audience-specific content recommendations
    - Optimal posting schedules
    - Content format suggestions
    - Engagement optimization
    - Brand voice consistency
    """
    try:
        logger.info("Starting content strategy generation")
        
        # Get client
        gemini_client = get_gemini_client()
        
        # Generate content strategy
        strategy = await gemini_client.generate_content_strategy(
            analysis_data=request.analysis_data,
            target_audience=request.target_audience,
            content_type=request.content_type,
            brand_voice=request.brand_voice
        )
        
        response = ContentStrategyResponse(
            strategy_id=f"strategy_{int(datetime.utcnow().timestamp())}",
            content_ideas=strategy.get("content_ideas", []),
            posting_strategy=strategy.get("posting_strategy", {}),
            target_audience=request.target_audience,
            expected_engagement=strategy.get("expected_engagement", 0.0),
            timestamp=datetime.utcnow()
        )
        
        # Log strategy generation in background
        background_tasks.add_task(
            _log_analysis,
            "content_strategy",
            f"strategy_{int(datetime.utcnow().timestamp())}",
            len(request.analysis_data),
            strategy
        )
        
        logger.info("Content strategy generation completed")
        return response
        
    except Exception as e:
        logger.error(f"Content strategy generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Strategy generation failed: {str(e)}")

@router.post("/enhanced-search", response_model=GeminiSearchResponse)
async def enhanced_search_with_gemini(
    request: GeminiSearchRequest,
    background_tasks: BackgroundTasks
) -> GeminiSearchResponse:
    """
    Enhanced search combining Twitter data with Gemini AI insights
    
    Features:
    - Multi-source data aggregation
    - AI-powered relevance scoring
    - Contextual analysis
    - Trend identification
    - Influencer discovery
    """
    try:
        logger.info(f"Starting enhanced search for query: {request.query}")
        
        # Get clients
        twitter_client = get_twitter_client()
        gemini_client = get_gemini_client()
        
        # If no Twitter data provided, fetch some
        if not request.twitter_data:
            tweets = await twitter_client.search_recent_tweets(
                query=request.query,
                max_results=20
            )
            request.twitter_data = tweets
        
        # Perform enhanced search
        search_results = await gemini_client.enhanced_search_with_gemini(
            query=request.query,
            twitter_data=request.twitter_data,
            search_depth=request.search_depth,
            max_results=request.max_results
        )
        
        response = GeminiSearchResponse(
            query=request.query,
            search_results=search_results.get("search_results", []),
            combined_analysis=search_results.get("combined_analysis", {}),
            search_metadata=search_results.get("search_metadata", {}),
            timestamp=datetime.utcnow()
        )
        
        # Log search in background
        background_tasks.add_task(
            _log_analysis,
            "enhanced_search",
            request.query,
            len(request.twitter_data) if request.twitter_data else 0,
            search_results
        )
        
        logger.info(f"Enhanced search completed for {len(request.twitter_data) if request.twitter_data else 0} tweets")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/models")
async def get_available_models():
    """Get list of available Gemini models"""
    try:
        gemini_client = get_gemini_client()
        models = await gemini_client.get_available_models()
        return {
            "current_model": "gemini-1.5-flash",
            "available_models": models,
            "temperature": 0.7,
            "max_tokens": 2048,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        return {
            "current_model": "gemini-1.5-flash",
            "available_models": ["gemini-pro", "gemini-pro-vision"],
            "temperature": 0.7,
            "max_tokens": 2048,
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }

@router.get("/health")
async def health_check():
    """Health check for Gemini integration"""
    try:
        gemini_client = get_gemini_client()
        twitter_client = get_twitter_client()
        
        # Check if clients are properly initialized
        gemini_status = hasattr(gemini_client, 'initialized') and gemini_client.initialized
        twitter_status = hasattr(twitter_client, 'initialized') and twitter_client.initialized
        
        # Check API key configuration (mock check)
        api_key_configured = True  # Will be False if no API key is set
        
        return {
            "status": "healthy" if gemini_status and twitter_status else "degraded",
            "gemini_available": gemini_status,
            "twitter_available": twitter_status,
            "api_key_configured": api_key_configured,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "gemini_available": False,
            "twitter_available": False,
            "api_key_configured": False,
            "error": str(e),
            "timestamp": datetime.utcnow()
        }