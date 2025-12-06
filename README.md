# Code Buddy

> **Your AI-powered coding companion for Claude Desktop**

[![GitHub stars](https://img.shields.io/github/stars/Abhi-vish/code-buddy)](https://github.com/Abhi-vish/code-buddy/stargazers)
[![License](https://img.shields.io/github/license/Abhi-vish/code-buddy)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

> **Project Status**: Work in Progress - Active Development

A powerful Model Context Protocol (MCP) server that provides AI assistants with comprehensive file system and development tools. Built to work seamlessly with Claude Desktop and other MCP-compatible clients.

**Note**: This project is under active development. Core features are functional, but some areas are still being refined and tested.

## Features

### File Operations
- Read, write, edit, delete files at any location
- Copy and move files with full path support
- Support for both absolute and relative paths

### Directory Management
- Create, list, delete directories
- Recursive directory tree visualization
- Navigate project structures easily

### Code Tools
- Analyze code structure and complexity
- Extract functions and classes
- Format code with Black
- Lint code with Ruff

### Search & Replace
- Search patterns across files
- Find and replace text
- Bulk find-and-replace operations

### Git Integration
- Git status, diff, log operations
- Support for external repositories
- Branch and commit management

### Command Execution
- Run shell commands in any directory
- Execute Python scripts
- Custom working directory support

## Demo

Watch the agent in action creating a motivational quote website:

https://github.com/user-attachments/assets/5bd48fab-73cc-4ea9-b28e-d52ff224fc2b

*The agent automatically created the full project structure, HTML, CSS, and JavaScript with working API integration.*

## Current Status & Roadmap

### ✅ Completed Features
- MCP server implementation with 23+ tools
- Claude Desktop integration
- File operations (read, write, edit, delete, copy, move)
- Directory management with tree visualization
- Git integration with external repository support
- Code analysis and formatting tools
- Search and replace functionality
- Command execution with custom working directories
- Real-time streaming responses
- Absolute path support for external projects

### 🚧 In Development
- CLI Agent (standalone interactive interface)
- Comprehensive test suite
- Error recovery mechanisms
- Performance optimizations
- Enhanced documentation and examples

### 📋 Planned Features
- Multi-language support beyond Python
- Database integration tools
- Docker and container management
- API testing tools
- Project scaffolding templates
- Plugin system for custom tools

## Installation

### Prerequisites
- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Claude Desktop (for MCP integration)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Abhi-vish/code-buddy.git
cd code-buddy
```

2. Install dependencies:
```bash
uv sync
```

3. Set up your OpenAI API key:
```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## Usage with Claude Desktop

### Configure Claude Desktop

1. Open your Claude Desktop configuration file:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the MCP server configuration:

```json
{
  "mcpServers": {
    "code-buddy": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\code-buddy",
        "run",
        "python",
        "-m",
        "src.server.main"
      ],
      "cwd": "C:\\path\\to\\code-buddy",
      "env": {
        "PROJECT_ROOT": "C:\\path\\to\\code-buddy",
        "ALLOW_EXTERNAL_PATHS": "true"
      }
    }
  }
}
```

3. Replace `C:\\path\\to\\code-buddy` with your actual project path

4. Restart Claude Desktop

5. Look for the hammer icon (🔨) in Claude Desktop - this indicates MCP tools are available

### Using the Tools

Once configured, you can ask Claude to:
- "Read the main.py file and explain what it does"
- "Create a new React app at C:\\Users\\Projects\\myapp"
- "Show me the git status of this project"
- "Format all Python files in the src directory"
- "Search for TODO comments in the codebase"

The agent will automatically use the appropriate tools to complete your requests.

## CLI Agent (In Development)

An interactive command-line interface is currently under development. This will provide a standalone way to interact with the coding agent without Claude Desktop.

```bash
# Coming soon
uv run python chat_agent.py
```

Features planned:
- Conversational interface with streaming responses
- Direct tool access from terminal
- Multi-project support
- Interactive debugging

## Available Tools

### File Tools
- `read_file` - Read file contents
- `write_file` - Write or create files
- `edit_file` - Find and replace content
- `delete_file` - Delete files
- `move_file` - Move or rename files
- `copy_file` - Copy files

### Directory Tools
- `create_directory` - Create directories
- `list_directory` - List directory contents
- `delete_directory` - Delete directories
- `get_directory_tree` - Get recursive tree structure

### Search Tools
- `search_in_files` - Search for patterns
- `find_replace` - Find and replace in a file
- `find_replace_all` - Bulk find and replace

### Code Tools
- `analyze_code` - Analyze code metrics
- `get_functions` - Extract function definitions
- `format_code` - Format with Black
- `lint_code` - Lint with Ruff

### Git Tools
- `git` - Run git commands
- `git_status` - Get repository status
- `git_diff` - Show changes
- `git_log` - View commit history

### Command Tools
- `run_command` - Execute shell commands
- `run_python` - Run Python scripts

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key (required for CLI agent)
- `PROJECT_ROOT` - Default project root directory
- `ALLOW_EXTERNAL_PATHS` - Enable access to files outside project root (default: `true`)
- `MAX_FILE_SIZE` - Maximum file size in bytes (default: 1MB)
- `MAX_DEPTH` - Maximum directory traversal depth (default: 4)
- `LOG_LEVEL` - Logging level (default: `INFO`)

### Server Configuration

Edit `config/default.yaml` to customize server behavior:

```yaml
name: "coding-agent"
version: "1.0.0"
max_file_size: 1048576  # 1MB
max_depth: 4
log_level: "INFO"
allow_external_paths: true
```

## Development

### Project Structure

```
code-buddy/
├── src/
│   ├── client/          # Client-side code (CLI agent)
│   │   ├── agents/      # Agent implementations
│   │   ├── llm/         # LLM integrations
│   │   └── ui/          # User interfaces
│   ├── server/          # MCP server implementation
│   │   ├── tools/       # Tool implementations
│   │   ├── resources/   # Resource providers
│   │   ├── prompts/     # Prompt templates
│   │   └── utils/       # Utility functions
│   └── shared/          # Shared code
├── config/              # Configuration files
├── assets/              # Demo videos and images
└── pyproject.toml       # Project dependencies
```

### Running Tests

```bash
# Run tests (coming soon)
uv run pytest
```

### Code Quality

```bash
# Format code
uv run black .

# Lint code
uv run ruff check .
```

## Troubleshooting

### Claude Desktop doesn't show tools
- Verify the configuration path is correct
- Check that `uv` is in your PATH
- Restart Claude Desktop completely
- Look for errors in Claude Desktop logs

### Commands hang or timeout
- Increase timeout in tool parameters
- Check if the command requires user input
- Verify file paths are correct

### Permission errors
- Ensure `ALLOW_EXTERNAL_PATHS` is set to `true`
- Check file system permissions
- Run with appropriate user privileges

## Known Issues & Limitations

- **edit_file tool**: Requires exact whitespace matching; use `write_file` for complex edits
- **Large files**: Files over 1MB may have performance issues
- **CLI Agent**: Still in development; use Claude Desktop for production use
- **Windows paths**: Use forward slashes or double backslashes in paths
- **Git operations**: Some git commands may require manual input handling

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with the [Model Context Protocol](https://modelcontextprotocol.io/)
- Powered by [OpenAI](https://openai.com/) and [Anthropic Claude](https://www.anthropic.com/)
- Uses [uv](https://github.com/astral-sh/uv) for fast Python package management

## Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section

---

**Note**: This is an active development project. Features and APIs may change. Contributions and feedback are welcome as we continue to improve and expand the tool suite.
