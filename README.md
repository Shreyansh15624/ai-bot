
# 🤖 AI CLI Agent: Autonomous Agentic Code Editor

## Description

A lightweight, terminal-native AI agent engineered to interface seamlessly with Google's Gemini models. Built in Python, this tool functions as a toy agentic code editor capable of reading, updating, and executing code autonomously. By utilizing a modular function-calling architecture and a dynamic ReAct (Reasoning and Acting) feedback loop, the agent can navigate local file systems, evaluate its own execution outputs (stdout/stderr), and iterate until a task is successfully resolved. 

## Motivation

Standard chat interfaces often lack the context and permissions necessary for real software development tasks. The motivation behind this project is to build an LLM-powered command-line program from scratch that bypasses these limitations. By providing the AI with direct filesystem access, dynamic script execution, and a self-correcting feedback loop, this agent serves as a transparent, high-speed alternative for local codebase manipulation and bug fixing. It prioritizes speed, deterministic dependency management, and secure state handling.

## Quick Start

### Prerequisites

* Python 3.14+
* `uv` package manager (`pip install uv`)
* Google Gemini API Key

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Shreyansh15624/ai-bot
cd ai-bot
```

2. **Initialize the environment:**
This project utilizes `uv` (`pyproject.toml` / `uv.lock`) for lightning-fast, fully deterministic dependency resolution.
```bash
uv sync
```

3. **Configure Environment Variables:**
Add your API key to your environment or a `.env` file:
```bash
export GOOGLE_GENAI_API_KEY="your_api_key_here"
```

## Usage

Execute natural language commands directly from your terminal. The agent will autonomously decide which tools from the `functions/` directory to use to accomplish your prompt. 

Target specific workspaces by pointing the agent to the `projects/` directory, which safely isolates target data from the core orchestrator.

**Analyze an Isolated Project:**
```bash
uv run main.py "Scan the projects/ directory and find the appropriate calculator project directory, and read the python files, then summarize how the compound interest is calculated."
```

**Autonomous Bug Fixing & Execution Loop:**
```bash
uv run main.py "Review projects/calculator/main.py, find any logical errors, fix them, and run the script to verify the output is correct."
```
*Note: The agent will capture the terminal output. If an error occurs during execution, it will read the traceback, self-correct the code, and retry until successful.*

## Contributing

The system cleanly separates the core orchestrator (`main.py`) from the modular toolsets (`functions/`) and test environments (`projects/`). 

* **To add a new tool (e.g., web scraping, Git commands):** Define a new Python script in the `functions/` directory. The orchestrator will automatically parse the function signature and expose it to the LLM's context window.
* **To add a new test workspace:** Create a new folder inside the `projects/` directory to act as an isolated sandbox for the agent to manipulate.
