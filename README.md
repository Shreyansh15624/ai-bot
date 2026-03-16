# AI CLI Agent: Extensible Function-Calling Framework

A lightweight, terminal-native AI agent engineered to interface seamlessly with Google's GenAI models. Designed for developers who need rapid, token-efficient AI interactions and dynamic tool execution directly from the command line, without the overhead of a web GUI.

## 🏗️ System Architecture & Features

- This agent is built on a modular architecture, prioritizing speed, extensibility, and clean state management.
- Dynamic Tool Registry (/functions): A modular directory structure allowing developers to drop in custom Python functions that the LLM can autonomously trigger based on context.
- Built-in Execution capabilities (/calculator): Includes an isolated arithmetic environment to demonstrate the agent's ability to parse complex logic and execute external scripts securely.
- Token-Aware Verbosity: Built-in --verbose flag for developers to monitor token usage and API payload structures in real-time.
- Modern Python Tooling: Built on Python 3.14 and leverages uv for lightning-fast, reproducible dependency resolution.

## 🚀 Quick Start

Prerequisites
- Python 3.14+
- `uv` package manager (`pip install uv`)
- Google Gemini API Key

Installation

1. Clone the repository:
```bash
git clone https://github.com/Shreyansh15624/ai-bot.git
cd ai-bot
```
2. Initialize the environment and install dependencies:
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt 
```
3. Configure Environment Variables:
```bash
# Create your .env file
touch .env
```
4. Add your Google GenAI key to the .env file:
```
GOOGLE_GENAI_API_KEY="your_api_key_here"
```

## 💻 Usage Examples

Execute natural language commands directly from your terminal.

Standard Execution:
```bash
python main.py "Calculate the compound interest on 5000 over 5 years at 4.5%"
```

Developer Mode (Token & State Inspection):
```bash
python main.py "Explain the concept of Retrieval-Augmented Generation" --verbose
```

## 🛠️ Extending the Agent

To add custom capabilities to the agent, define a new tool in the /functions directory. Then in the core main.py file register the function signature and expose it to the LLM's decision-making logic.
