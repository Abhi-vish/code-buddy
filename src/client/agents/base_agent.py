from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from src.client.llm import BaseLLM, Message


@dataclass
class AgentConfig:
    max_iterations: int = 10
    system_prompt: str = ""
    verbose: bool = False
    temperature: float = 0.7


@dataclass
class AgentState:
    messages: list[Message] = field(default_factory=list)
    iteration: int = 0
    is_complete: bool = False
    final_response: str | None = None


class BaseAgent(ABC):
    
    def __init__(self, llm: BaseLLM, config: AgentConfig | None = None):
        self.llm = llm
        self.config = config or AgentConfig()
        self.state = AgentState()
    
    @abstractmethod
    async def run(self, user_input: str) -> str:
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        pass
    
    def reset(self):
        self.state = AgentState()
    
    def add_message(self, role: str, content: str):
        self.state.messages.append(Message(role=role, content=content))
    
    def get_messages(self) -> list[Message]:
        return self.state.messages.copy()