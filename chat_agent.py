#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.client.session import MCPSessionManager
from src.client.llm import OpenAILLM
from src.client.agents import CodingAgent, AgentConfig


async def run_interactive_agent():
    print("=" * 70)
    print("  Interactive Coding Agent")
    print("=" * 70)
    print("\nInitializing agent with MCP tools...")
    
    manager = MCPSessionManager.create(
        project_root=Path(__file__).parent,
        server_module="src.server.main"
    )
    
    llm = OpenAILLM(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=4096
    )
    
    async with manager.connect() as session:
        config = AgentConfig(
            max_iterations=10,
            verbose=True
        )
        agent = CodingAgent(llm, session, config)
        await agent.initialize()
        
        print(f"Agent initialized with {len(agent.tools)} tools available")
        print("\nType your questions or requests. Type 'exit' or 'quit' to end.")
        print("Type 'help' for available commands.\n")
        
        conversation_history = []
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\nGoodbye!")
                    break
                
                if user_input.lower() in ['help', '?']:
                    print_help(agent)
                    continue
                
                if user_input.lower() == 'tools':
                    print_tools(agent)
                    continue
                
                if user_input.lower() == 'clear':
                    conversation_history = []
                    print("\nConversation history cleared.")
                    continue
                
                print()
                async for chunk in agent.chat_stream(user_input):
                    print(chunk, end='', flush=True)
                print()
                
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")


def print_help(agent):
    print("\n" + "=" * 70)
    print("  HELP")
    print("=" * 70)
    print("""
Commands:
  help, ?     - Show this help message
  tools       - List all available tools
  clear       - Clear conversation history
  exit, quit  - Exit the agent

Usage:
  Just type your question or request naturally. The agent will:
  - Answer questions about code
  - Read and analyze files
  - Make changes to files
  - Run commands
  - Use git operations
  - Format and lint code
  - Search for patterns
  - And more

Examples:
  "What files are in the src directory?"
  "Read the main.py file"
  "Search for the function called 'process_data'"
  "Run the tests"
  "Show me the git status"
  "Format all Python files"
    """)


def print_tools(agent):
    print("\n" + "=" * 70)
    print(f"  AVAILABLE TOOLS ({len(agent.tools)})")
    print("=" * 70)
    
    categories = {
        "File Operations": [],
        "Directory Operations": [],
        "Search & Replace": [],
        "Git Operations": [],
        "Code Tools": [],
        "Command Execution": []
    }
    
    for tool in agent.tools:
        name = tool['name']
        desc = tool.get('description', 'No description')
        
        if 'file' in name:
            categories["File Operations"].append((name, desc))
        elif 'directory' in name or 'tree' in name or 'list' in name:
            categories["Directory Operations"].append((name, desc))
        elif 'search' in name or 'find' in name or 'replace' in name:
            categories["Search & Replace"].append((name, desc))
        elif 'git' in name:
            categories["Git Operations"].append((name, desc))
        elif 'analyze' in name or 'format' in name or 'lint' in name or 'functions' in name:
            categories["Code Tools"].append((name, desc))
        elif 'command' in name or 'run' in name or 'python' in name:
            categories["Command Execution"].append((name, desc))
        else:
            categories["File Operations"].append((name, desc))
    
    for category, tools in categories.items():
        if tools:
            print(f"\n{category}:")
            for name, desc in sorted(tools):
                print(f"  {name:25s} - {desc}")
    
    print()


def main():
    try:
        asyncio.run(run_interactive_agent())
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
