# Twitter Agent

An AI-powered Twitter automation agent that combines Fetch.ai, ChatGPT, and Composio to provide intelligent Twitter data extraction, analysis, and automation capabilities.

## 🚀 Features

### Core Capabilities
- **Natural Language Processing**: Convert natural language requests into structured Twitter operations
- **Intelligent Data Extraction**: Search, filter, and analyze tweets with AI-powered insights
- **Automated Workflows**: Predefined workflows for common Twitter operations
- **Real-time Monitoring**: Monitor users, topics, and trends automatically
- **Sentiment Analysis**: AI-powered sentiment analysis of tweets and conversations
- **Content Curation**: Automatically curate and share relevant content
- **Engagement Boosting**: Smart engagement strategies for your tweets

### Twitter Operations
- Search recent tweets and full archive
- Get user timelines and profiles
- Create, like, retweet, and reply to tweets
- Follow/unfollow users
- Manage lists and bookmarks
- Monitor trends and hashtags
- Analyze engagement metrics
- Schedule posts and automation

### AI Integration
- **GPT-4**: Task planning, content analysis, and natural language responses
- **Fetch.ai**: Autonomous agent orchestration and scheduling (with fallback)
- **Composio**: Twitter API integration and tool management (with fallback)
- **Hybrid Architecture**: Graceful degradation when external services are unavailable

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │   GPT Planner   │    │  Task Executor  │
│  (Natural Lang) │───▶│  (Task Planning)│───▶│  (Workflow)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │    │  Twitter Client │    │   Scheduler     │
│   (React UI)    │◀───│  (Composio +    │◀───│  (Fetch.ai +    │
└─────────────────┘    │   Direct API)   │    │   Local)        │
                       └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Composio      │    │   Fetch.ai      │
                       │   (Twitter API) │    │   (Autonomous)  │
                       └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Twitter API v2 access
- OpenAI API key
- Fetch.ai account (optional - provides autonomous agent capabilities)
- Composio account (optional - provides enhanced Twitter API integration)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/twitter-agent.git
cd twitter-agent
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd ui
npm install
```

### 4. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
nano .env
```

Required environment variables:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Twitter API Configuration
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# Optional: Fetch.ai Configuration
FETCH_AI_API_KEY=your_fetch_ai_api_key_here
FETCH_AI_AGENT_ID=your_fetch_ai_agent_id_here

# Optional: Composio Configuration
COMPOSIO_API_KEY=your_composio_api_key_here
```

## 🚀 Quick Start

### 1. Start the Backend
```bash
# Start the FastAPI server
python main.py
```

### 2. Start the Frontend
```bash
cd ui
npm run dev
```

### 3. Access the Dashboard
Open your browser and navigate to `http://localhost:3000`

### 5. Test Integrations (Optional)
```bash
# Test Fetch.ai and Composio integrations
python examples/test_integrations.py
```

## 📖 Usage Examples

### Natural Language Requests
```python
from agent.core_agent import TwitterAgent

agent = TwitterAgent()

# Search for tweets about AI
result = await agent.process_natural_language_request(
    "Find the latest 50 tweets about artificial intelligence and analyze sentiment"
)

# Monitor a user
result = await agent.process_natural_language_request(
    "Monitor @elonmusk for tweets about AI and auto-bookmark high engagement posts"
)

# Analyze trends
result = await agent.process_natural_language_request(
    "Analyze trending topics about Web3 in the last 24 hours"
)
```

### Direct API Usage
```python
# Search tweets
tweets = await agent.search_tweets(
    query="Bitcoin",
    max_results=100,
    start_time=datetime.utcnow() - timedelta(hours=24)
)

# Analyze trends
trends = await agent.analyze_trends("Ethereum", "7d")

# Create automated post
post_id = await agent.create_automated_post(
    "Exciting developments in AI! #AI #Innovation"
)
```

### Workflow Management
```python
from workflows.workflow_manager import WorkflowManager

workflow_manager = WorkflowManager(agent)

# Execute a predefined workflow
result = await workflow_manager.execute_workflow(
    "trend_monitor",
    {"topics": ["AI", "Machine Learning"], "max_tweets": 200}
)

# Schedule recurring workflow
task_id = await workflow_manager.schedule_workflow(
    "user_monitor",
    {"username": "elonmusk", "keywords": ["AI", "Tesla"]},
    {"interval": 3600}  # Run every hour
)
```

## 🔧 Configuration

### Agent Settings
```python
# config/settings.py
class Settings:
    # Rate limiting
    MAX_TWEETS_PER_REQUEST = 100
    RATE_LIMIT_DELAY = 1.0
    
    # GPT settings
    GPT_MODEL = "gpt-4"
    GPT_TEMPERATURE = 0.7
    MAX_TOKENS = 2000
    
    # Scheduling
    DEFAULT_SCHEDULE_INTERVAL = 3600  # 1 hour
    MAX_RETRIES = 3
```

### Workflow Configuration
```json
{
  "name": "Custom Workflow",
  "description": "Monitor specific topics",
  "type": "recurring",
  "schedule": {
    "interval": 1800,
    "max_runs": null
  },
  "parameters": {
    "topics": ["AI", "Web3"],
    "max_tweets": 100
  }
}
```

## 📊 Dashboard Features

### Overview Tab
- Real-time agent status
- Task queue management
- Recent activity feed
- Performance metrics

### Workflows Tab
- Predefined workflow library
- Custom workflow creation
- Schedule management
- Execution monitoring

### Tasks Tab
- Task queue visualization
- Progress tracking
- Error handling
- Manual task control

### Settings Tab
- API configuration
- Agent parameters
- Notification settings
- Security options

## 🔌 API Endpoints

### Agent Management
```bash
# Get agent status
GET /api/agent/status

# Start agent
POST /api/agent/start

# Stop agent
POST /api/agent/stop
```

### Workflow Management
```bash
# List workflows
GET /api/workflows

# Execute workflow
POST /api/workflows/execute
{
  "workflow_name": "trend_monitor",
  "parameters": {"topics": ["AI"]}
}

# Schedule workflow
POST /api/workflows/schedule
{
  "workflow_name": "user_monitor",
  "parameters": {"username": "elonmusk"},
  "schedule_config": {"interval": 3600}
}
```

### Task Management
```bash
# Get task queue
GET /api/tasks

# Create task
POST /api/tasks
{
  "type": "search_tweets",
  "parameters": {"query": "Bitcoin"}
}

# Cancel task
DELETE /api/tasks/{task_id}
```

## 🧪 Testing

### Run Tests
```bash
# Backend tests
python -m pytest tests/

# Frontend tests
cd ui
npm test
```

### Example Test Cases
```python
# test_agent.py
import pytest
from agent.core_agent import TwitterAgent

@pytest.mark.asyncio
async def test_search_tweets():
    agent = TwitterAgent()
    result = await agent.search_tweets("test query", max_results=10)
    assert result["tweet_count"] <= 10
    assert "tweets" in result
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Production Setup
```bash
# Install production dependencies
pip install -r requirements-prod.txt

# Configure production settings
export DEBUG=false
export LOG_LEVEL=INFO

# Start with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📈 Monitoring

### Logs
```bash
# View agent logs
tail -f logs/agent.log

# View workflow logs
tail -f logs/workflows.log
```

### Metrics
- Task execution times
- API rate limit usage
- Error rates
- Workflow success rates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Documentation: [Wiki](https://github.com/yourusername/twitter-agent/wiki)
- Issues: [GitHub Issues](https://github.com/yourusername/twitter-agent/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/twitter-agent/discussions)

## 🙏 Acknowledgments

- [Fetch.ai](https://fetch.ai/) for autonomous agent framework
- [OpenAI](https://openai.com/) for GPT integration
- [Composio](https://composio.dev/) for Twitter API tools
- [Twitter API](https://developer.twitter.com/) for social media data

## 🔮 Roadmap

- [ ] Multi-platform support (LinkedIn, Instagram)
- [ ] Advanced AI models integration
- [ ] Real-time streaming capabilities
- [ ] Mobile app development
- [ ] Enterprise features
- [ ] Plugin system for custom workflows

---

**Note**: This project is for educational and research purposes. Please ensure compliance with Twitter's Terms of Service and API usage policies.
