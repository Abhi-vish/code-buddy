from src.client.llm import BaseLLM, Message, LLMResponse
from src.client.session import MCPSession
from .base_agent import BaseAgent, AgentConfig, AgentState
from .tool_executor import ToolExecutor, ToolExecutionResult


SYSTEM_PROMPT = """You are a coding assistant with access to tools for reading, writing, and managing code files.

Available capabilities:
- Read and write files
- Search and replace in files
- Run shell commands
- Git operations
- Code analysis and formatting

When asked to perform a task:
1. Understand the request
2. Use appropriate tools to gather information
3. Make necessary changes
4. Verify the changes if needed
5. Provide a clear summary of what was done

Always explain your actions and reasoning."""


class CodingAgent(BaseAgent):
    
    def __init__(
        self,
        llm: BaseLLM,
        session: MCPSession,
        config: AgentConfig | None = None
    ):
        super().__init__(llm, config)
        self.session = session
        self.tool_executor = ToolExecutor(session)
        self.tools = []
        self.available_resources = []
    
    async def initialize(self):
        tools_response = await self.session.list_tools()
        self.tools = self._convert_tools(tools_response.tools)
        
        resources_response = await self.session.list_resources()
        self.available_resources = [r.uri for r in resources_response.resources]
    
    def _convert_tools(self, mcp_tools) -> list[dict]:
        tools = []
        for tool in mcp_tools:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        return tools
    
    def get_system_prompt(self) -> str:
        if self.config.system_prompt:
            return self.config.system_prompt
        
        resources_info = "\n".join(f"- {uri}" for uri in self.available_resources[:20])
        extra = "\n- ..." if len(self.available_resources) > 20 else ""
        
        return f"""{SYSTEM_PROMPT}

Available resources:
{resources_info}{extra}"""
    
    async def run(self, user_input: str) -> str:
        self.reset()
        self.add_message("system", self.get_system_prompt())
        self.add_message("user", user_input)
        
        while self.state.iteration < self.config.max_iterations:
            self.state.iteration += 1
            
            response = await self.llm.chat(
                messages=self.state.messages,
                tools=self.tools if self.tools else None
            )
            
            if response.tool_calls:
                await self._handle_tool_calls(response)
            else:
                self.state.is_complete = True
                self.state.final_response = response.content
                break
        
        return self.state.final_response or "Max iterations reached"
    
    async def _handle_tool_calls(self, response: LLMResponse):
        assistant_message = Message(role="assistant", content=response.content or "")
        assistant_message.tool_calls = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.name,
                    "arguments": str(tc.arguments)
                }
            }
            for tc in response.tool_calls
        ]
        self.state.messages.append(assistant_message)
        
        results = await self.tool_executor.execute_all(response.tool_calls)
        
        for result in results:
            if self.config.verbose:
                print(f"[Tool: {result.tool_name}]")
                preview = result.result[:200] + "..." if len(result.result) > 200 else result.result
                print(f"[Result: {preview}]")
            
            tool_message = Message(role="tool", content=result.result)
            tool_message.tool_call_id = result.tool_call_id
            self.state.messages.append(tool_message)
    
    async def chat(self, user_input: str) -> str:
        if not self.state.messages:
            self.add_message("system", self.get_system_prompt())
        
        self.add_message("user", user_input)
        
        response = await self.llm.chat(
            messages=self.state.messages,
            tools=self.tools if self.tools else None
        )
        
        iteration = 0
        while response.tool_calls and iteration < self.config.max_iterations:
            iteration += 1
            await self._handle_tool_calls(response)
            
            response = await self.llm.chat(
                messages=self.state.messages,
                tools=self.tools
            )
        
        if response.content:
            self.add_message("assistant", response.content)
        
        return response.content or "No response"
    
    async def chat_stream(self, user_input: str):
        if not self.state.messages:
            self.add_message("system", self.get_system_prompt())
        
        self.add_message("user", user_input)
        
        response = await self.llm.chat(
            messages=self.state.messages,
            tools=self.tools if self.tools else None
        )
        
        iteration = 0
        while response.tool_calls and iteration < self.config.max_iterations:
            iteration += 1
            await self._handle_tool_calls(response)
            
            response = await self.llm.chat(
                messages=self.state.messages,
                tools=self.tools
            )
        
        if response.tool_calls:
            if response.content:
                yield response.content
            return
        
        full_response = ""
        async for chunk in self.llm.chat_stream(
            messages=self.state.messages,
            tools=None
        ):
            full_response += chunk
            yield chunk
        
        if full_response:
            self.add_message("assistant", full_response)


class CodingAgentBuilder:
    
    def __init__(self):
        self._llm = None
        self._session = None
        self._config = AgentConfig()
    
    def with_llm(self, llm: BaseLLM):
        self._llm = llm
        return self
    
    def with_session(self, session: MCPSession):
        self._session = session
        return self
    
    def with_config(self, config: AgentConfig):
        self._config = config
        return self
    
    def with_max_iterations(self, max_iterations: int):
        self._config.max_iterations = max_iterations
        return self
    
    def with_system_prompt(self, prompt: str):
        self._config.system_prompt = prompt
        return self
    
    def verbose(self, enabled: bool = True):
        self._config.verbose = enabled
        return self
    
    async def build(self) -> CodingAgent:
        if not self._llm:
            raise ValueError("LLM is required")
        if not self._session:
            raise ValueError("Session is required")
        
        agent = CodingAgent(self._llm, self._session, self._config)
        await agent.initialize()
        return agent