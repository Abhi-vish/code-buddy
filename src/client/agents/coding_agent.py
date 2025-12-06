from src.client.llm import BaseLLM, Message, LLMResponse
from src.client.session import MCPSession
from .base_agent import BaseAgent, AgentConfig, AgentState
from .tool_executor import ToolExecutor, ToolExecutionResult


SYSTEM_PROMPT = """You are a helpful coding assistant with access to file and code tools.

IMPORTANT RULES:

1. ALWAYS COMMUNICATE FIRST
   - Before using any tool, briefly explain what you're about to do
   - Example: "Let me read the main.py file to check the code..."
   - Example: "I'll search for that function in the codebase..."

2. USE TOOLS TO READ FILES - NEVER ASK FOR CODE
   - When user mentions a file, USE read_file tool to read it
   - NEVER say "please provide the code" or "can you share the file"
   - You have full access to the project - just read the files yourself
   - Example: User says "fix the bug in index.js" → You read index.js first

3. WORKING WITH ABSOLUTE PATHS (CRITICAL!)
   - When user provides an absolute path (C:\\, /home/, etc), use it EXACTLY as given
   - When get_directory_tree returns files, construct FULL paths for reading them
   - Example: get_directory_tree("C:\\project") returns "index.html"
     → read_file("C:\\project\\index.html") NOT just "index.html"
   - ALWAYS combine directory path + filename when working with external directories
   - Use forward slashes (/) or double backslashes (\\\\) in Windows paths
   - For git and run_command tools: ALWAYS pass the cwd parameter when working outside project
   - Example: git("init", cwd="C:\\project") NOT just git("init")

4. BE PROACTIVE
   - Read files to understand context before answering
   - Search codebase when looking for something
   - Check file structure with get_tree when needed

5. RESPOND NATURALLY
   - For general questions, just answer without tools
   - For coding tasks, read relevant files first then help
   - Be concise and helpful

6. FILE EDITING STRATEGY
   - For small changes (1-2 lines): Try edit_file with EXACT content match
   - If edit_file fails: Use write_file to rewrite the entire file
   - NEVER retry edit_file multiple times - switch to write_file after first failure
   - edit_file requires EXACT whitespace/indentation match - it's very strict
   - write_file is more reliable for complex changes

WORKFLOW FOR CODE TASKS:
1. Say what you're going to do
2. Use read_file to get the code (with FULL absolute path if working outside project)
3. Analyze and provide solution
4. Use write_file or edit_file to make changes if needed
5. Confirm what was done

PROJECT: {project_root}"""

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
                print(f"\n[Tool: {result.tool_name}]", flush=True)
                preview = result.result[:200] + "..." if len(result.result) > 200 else result.result
                print(f"[Result: {preview}]\n", flush=True)
            
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