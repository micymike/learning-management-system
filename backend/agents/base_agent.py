from abc import ABC, abstractmethod
from typing import Dict, Any, List
import asyncio
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AgentMessage:
    sender: str
    receiver: str
    content: Dict[str, Any]
    message_type: str

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.status = AgentStatus.IDLE
        self.message_queue = asyncio.Queue()
        self.results = {}
        
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    async def send_message(self, receiver: str, content: Dict[str, Any], message_type: str = "data"):
        message = AgentMessage(self.name, receiver, content, message_type)
        return message
    
    async def receive_message(self, message: AgentMessage):
        await self.message_queue.put(message)
    
    async def start(self):
        self.status = AgentStatus.WORKING
        while self.status == AgentStatus.WORKING:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                result = await self.process(message.content)
                self.results[message.sender] = result
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.status = AgentStatus.ERROR
                self.results['error'] = str(e)