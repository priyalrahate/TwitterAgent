"""
Task models for Twitter Agent
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class AgentTask:
    """Represents a task for the Twitter agent"""
    id: str
    type: str
    parameters: Dict[str, Any]
    status: str = "pending"
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()