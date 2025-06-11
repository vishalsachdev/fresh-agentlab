import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import anthropic
import openai
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / '.env')

class BaseAgent(ABC):
    def __init__(self, config: Dict[str, Any], agent_type: str):
        self.agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"
        self.agent_type = agent_type
        self.config = config
        self.status = "initialized"
        self.current_task = None
        self.performance_metrics = {
            "tasks_completed": 0,
            "success_rate": 0.0,
            "avg_response_time": 0.0
        }
        self.last_activity = datetime.now()
        
        # Debug: Check if environment variables are loaded
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
        self.openai_client = openai.OpenAI(api_key=openai_key)
        
    async def get_ai_response(self, prompt: str, model_provider: str = None) -> str:
        provider = model_provider or self.config["models"]["default_provider"]
        
        try:
            if provider == "anthropic":
                response = self.anthropic_client.messages.create(
                    model=self.config["models"]["anthropic_model"],
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            elif provider == "openai":
                response = self.openai_client.chat.completions.create(
                    model=self.config["models"]["openai_model"],
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4000
                )
                return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"AI response error: {str(e)}")
    
    def update_status(self, status: str, current_task: str = None):
        self.status = status
        self.current_task = current_task
        self.last_activity = datetime.now()
    
    def update_metrics(self, task_completed: bool, response_time: float):
        self.performance_metrics["tasks_completed"] += 1
        if task_completed:
            current_success = self.performance_metrics["success_rate"]
            total_tasks = self.performance_metrics["tasks_completed"]
            self.performance_metrics["success_rate"] = (
                (current_success * (total_tasks - 1) + 1.0) / total_tasks
            )
        
        current_avg = self.performance_metrics["avg_response_time"]
        total_tasks = self.performance_metrics["tasks_completed"]
        self.performance_metrics["avg_response_time"] = (
            (current_avg * (total_tasks - 1) + response_time) / total_tasks
        )
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "current_task": self.current_task,
            "performance_metrics": self.performance_metrics,
            "last_activity": self.last_activity.isoformat()
        }
    
    @abstractmethod
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        pass