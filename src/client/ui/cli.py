import asyncio
import sys
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class CLIConfig:
    model: str = "gpt-4o-mini"
    project_root: Path = None
    max_iterations: int = 15
    temperature: float = 0.7
    verbose: bool = False


class OpenAICLI:
    
    def __init__(self, config: CLIConfig):
        self.config = config
        self.agent = None
        self.session = None
        self.running = True
    
    async def initialize(self, session):
        from src.client.llm import OpenAILLM
        from src.client.agents import CodingAgent, AgentConfig
        
        self.session = session
        
        llm = OpenAILLM(
            model=self.config.model,
            temperature=self.config.temperature
        )
        
        agent_config = AgentConfig(
            max_iterations=self.config.max_iterations,
            verbose=self.config.verbose
        )
        
        self.agent = CodingAgent(llm, session, agent_config)
        await self.agent.initialize()
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        width = 60
        print("=" * width)
        print("CODING AGENT".center(width))
        print(f"Model: {self.config.model}".center(width))
        print("=" * width)
        print(f"Project: {self.config.project_root}")
        print("-" * width)
        print("Commands:")
        print("  /help     Show this help")
        print("  /clear    Clear screen")
        print("  /reset    Reset conversation")
        print("  /tools    List available tools")
        print("  /files    List project files")
        print("  /tree     Show project structure")
        print("  /exit     Exit the agent")
        print("-" * width)
        print()
    
    def print_help(self):
        print()
        print("Available Commands:")
        print("  /help     Show this help message")
        print("  /clear    Clear the screen")
        print("  /reset    Reset the conversation history")
        print("  /tools    List all available tools")
        print("  /files    List project files (first 30)")
        print("  /tree     Show project directory structure")
        print("  /read     Read a file: /read <filepath>")
        print("  /run      Run a command: /run <command>")
        print("  /exit     Exit the application")
        print()
        print("Tips:")
        print("  - Ask the agent to read, write, or modify files")
        print("  - Ask for code reviews, refactoring, or debugging help")
        print("  - The agent can run shell commands and git operations")
        print()
    
    async def handle_command(self, command: str) -> bool:
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd in ("/exit", "/quit", "/q"):
            self.running = False
            return True
        
        if cmd == "/help":
            self.print_help()
            return True
        
        if cmd == "/clear":
            self.clear_screen()
            self.print_header()
            return True
        
        if cmd == "/reset":
            self.agent.reset()
            await self.agent.initialize()
            print("\nConversation reset.\n")
            return True
        
        if cmd == "/tools":
            tools = await self.session.list_tools()
            print(f"\nAvailable Tools ({len(tools.tools)}):\n")
            for tool in tools.tools:
                desc = tool.description[:50] + "..." if len(tool.description) > 50 else tool.description
                print(f"  {tool.name:<20} {desc}")
            print()
            return True
        
        if cmd == "/files":
            resources = await self.session.list_resources()
            files = [r.uri.replace("file://", "") for r in resources.resources if r.uri.startswith("file://")]
            print(f"\nProject Files ({len(files)} total):\n")
            for f in files[:30]:
                print(f"  {f}")
            if len(files) > 30:
                print(f"  ... and {len(files) - 30} more")
            print()
            return True
        
        if cmd == "/tree":
            result = await self.session.call_tool("get_tree", {"max_depth": 3})
            print(f"\n{result.content[0].text}\n")
            return True
        
        if cmd == "/read":
            if not args:
                print("\nUsage: /read <filepath>\n")
                return True
            result = await self.session.call_tool("read_file", {"filepath": args})
            print(f"\n{result.content[0].text}\n")
            return True
        
        if cmd == "/run":
            if not args:
                print("\nUsage: /run <command>\n")
                return True
            result = await self.session.call_tool("run_command", {"command": args, "timeout": 30})
            print(f"\n{result.content[0].text}\n")
            return True
        
        print(f"\nUnknown command: {cmd}")
        print("Type /help for available commands.\n")
        return True
    
    def print_thinking(self):
        print("\nThinking", end="", flush=True)
    
    def print_tool_call(self, tool_name: str, args: dict):
        if self.config.verbose:
            print(f"\n[Tool: {tool_name}]")
            for key, value in args.items():
                val_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                print(f"  {key}: {val_str}")
    
    async def process_input(self, user_input: str):
        if user_input.startswith("/"):
            await self.handle_command(user_input)
            return
        
        print()
        
        try:
            response = await self.agent.chat(user_input)
            print(f"Agent: {response}\n")
        except KeyboardInterrupt:
            print("\n\nInterrupted.\n")
        except Exception as e:
            print(f"\nError: {e}\n")
    
    async def run(self):
        from src.client.session import MCPSessionManager
        
        manager = MCPSessionManager(
            server_command=sys.executable,
            server_args=["-m", "src.server.main"],
            env={"PROJECT_ROOT": str(self.config.project_root)}
        )
        
        print("\nConnecting to MCP server...")
        
        async with manager.connect() as session:
            await self.initialize(session)
            
            self.clear_screen()
            self.print_header()
            
            while self.running:
                try:
                    user_input = input("You: ").strip()
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print("\n")
                    continue
                
                if not user_input:
                    continue
                
                await self.process_input(user_input)
            
            print("\nGoodbye!\n")


def run_openai_cli(
    model: str = "gpt-4o-mini",
    project_root: str | None = None,
    verbose: bool = False,
    temperature: float = 0.7
):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY=sk-xxxxx")
        sys.exit(1)
    
    config = CLIConfig(
        model=model,
        project_root=Path(project_root) if project_root else Path.cwd(),
        verbose=verbose,
        temperature=temperature
    )
    
    cli = OpenAICLI(config)
    asyncio.run(cli.run())


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Coding Agent CLI with OpenAI GPT-4o-mini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.client.ui.openai_cli
  python -m src.client.ui.openai_cli --project /path/to/project
  python -m src.client.ui.openai_cli --model gpt-4o --verbose
        """
    )
    
    parser.add_argument(
        "--model", "-m",
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    
    parser.add_argument(
        "--project", "-p",
        default=None,
        help="Project root directory (default: current directory)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output including tool calls"
    )
    
    parser.add_argument(
        "--temperature", "-t",
        type=float,
        default=0.7,
        help="Model temperature (default: 0.7)"
    )
    
    args = parser.parse_args()
    
    run_openai_cli(
        model=args.model,
        project_root=args.project,
        verbose=args.verbose,
        temperature=args.temperature
    )


if __name__ == "__main__":
    main()