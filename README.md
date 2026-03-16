# 🤖 AI CLI Agent: Extensible File-System & Execution Framework

A lightweight, terminal-native AI agent engineered to interface seamlessly with Google's GenAI models. Designed for developers and system administrators, this tool bypasses standard chat interfaces to provide an AI with autonomous filesystem access, dynamic script execution, and a modular function-calling architecture directly from the command line.

## 🏗️ System Architecture & Capabilities

This agent is built on a modular, tool-use architecture, prioritizing speed, deterministic dependency management, and secure state handling.

### 1. Autonomous Filesystem & Execution Tools

The core LLM is augmented with a suite of native tools injected via the `/functions` directory, allowing it to autonomously:

* **`get_files_info.py` / `get_file_content.py`:** Read and map directory structures and ingest file contents into its context window.
* **`write_file.py`:** Generate and write code, configurations, or logs directly to the local filesystem.
* **`run_python_file.py`:** Execute Python scripts dynamically based on generated outputs or user prompts.

### 2. Deterministic Tooling

* **Modern Package Management:** Built on Python 3.14+ utilizing `uv` (`pyproject.toml` / `uv.lock`) for lightning-fast, reproducible dependency resolution across environments.

## 📂 Repository Structure

The system cleanly separates the core orchestrator from the modular toolsets and test environments.

```text
├── functions/              # Dynamically injected agent capabilities
│   ├── get_file_content.py # Reads specific files
│   ├── get_files_info.py   # Scans directory trees
│   ├── write_file.py       # Writes to the filesystem
│   ├── run_python_file.py  # Executes scripts
│   └── config.py           # Tool configuration and state
├── calculator/             # Isolated arithmetic & execution sandbox
├── main.py                 # Core AI orchestrator and CLI entry point
├── tests.py                # Unit and integration test suite
├── pyproject.toml          # Project metadata and dependencies
└── uv.lock                 # Deterministic dependency lockfile

```

## 🚀 Quick Start & Execution

### Prerequisites

* Python 3.14+
* `uv` package manager (`pip install uv`)
* Google Gemini API Key

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Shreyansh15624/ai-bot.git
cd ai-bot

```


2. **Initialize the environment:**
Because this project uses `uv.lock`, dependency installation is fully deterministic.
```bash
uv sync

```


3. **Configure Environment Variables:**
Add your API key to your environment or a `.env` file:
```bash
export GOOGLE_GENAI_API_KEY="your_api_key_here"

```



## 💻 Usage Examples

Execute natural language commands directly from your terminal.

**Filesystem Mapping:**

```bash
uv run main.py "Scan the current directory and summarize the Python files."

```

**Code Generation & Execution:**

```bash
uv run main.py "Write a python script that calculates the Fibonacci sequence up to 100, save it, and run it."

```

## 🛠️ Extending the Agent

To add custom capabilities (e.g., Docker container management, API fetching), define a new tool in the `/functions` directory. The core `main.py` orchestrator will automatically parse the function signature and expose it to the LLM's tool-use logic.
