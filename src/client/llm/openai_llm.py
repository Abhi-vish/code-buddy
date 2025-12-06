import os
import json
from typing import AsyncIterator
from .base import BaseLLM, Message, ToolCall, LLMResponse
from dotenv import load_dotenv

load_dotenv()


class OpenAILLM(BaseLLM):
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client = None
        self._async_client = None
    
    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client
    
    @property
    def async_client(self):
        if self._async_client is None:
            from openai import AsyncOpenAI
            self._async_client = AsyncOpenAI(api_key=self.api_key)
        return self._async_client
    
    def _convert_messages(self, messages: list[Message]) -> list[dict]:
        converted = []
        for msg in messages:
            if msg.role == "tool":
                converted.append({
                    "role": "tool",
                    "content": msg.content,
                    "tool_call_id": getattr(msg, "tool_call_id", "unknown")
                })
            elif msg.role == "assistant" and hasattr(msg, "tool_calls"):
                converted.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": msg.tool_calls
                })
            else:
                converted.append({
                    "role": msg.role,
                    "content": msg.content
                })
        return converted
    
    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None
    ) -> LLMResponse:
        converted_messages = self._convert_messages(messages)
        
        kwargs = {
            "model": self.model,
            "messages": converted_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        response = await self.async_client.chat.completions.create(**kwargs)
        message = response.choices[0].message
        
        tool_calls = None
        if message.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                )
                for tc in message.tool_calls
            ]
        
        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=response.choices[0].finish_reason
        )
    
    async def chat_stream(
        self,
        messages: list[Message],
        tools: list[dict] | None = None
    ) -> AsyncIterator[str]:
        converted_messages = self._convert_messages(messages)
        
        kwargs = {
            "model": self.model,
            "messages": converted_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": True
        }
        
        stream = await self.async_client.chat.completions.create(**kwargs)
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content