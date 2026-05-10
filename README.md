# AegisAgent: The Sandboxed Autonomous AI Coder

![Python Version](https://img.shields.io/badge/python-3.14%2B-blue)
![Architecture](https://img.shields.io/badge/Architecture-ReAct_Loop-8A2BE2)
![Engines](https://img.shields.io/badge/Engines-Gemini_|_Ollama-FF8C00)
![Security](https://img.shields.io/badge/Security-Strict_Sandboxing-brightgreen)
![Package Manager](https://img.shields.io/badge/Package_Manager-uv-purple)

## Description

AegisAgent (formerly ai-bot) is a highly modular, terminal-native AI agent engineered to manipulate, execute, and debug code autonomously. Built with a dynamic **ReAct (Reasoning and Acting)** feedback loop, the agent doesn't just write code—it actively tests it, reads the standard output/error traces, and self-corrects until the objective is achieved. 

The architecture features a robust dual-engine system, allowing seamless switching between cloud-based reasoning (Google Gemini) and local, privacy-first execution (Ollama). To ensure host system integrity, the agent's file system access is strictly constrained by a cryptographic path-resolution sandbox, neutralizing directory traversal vulnerabilities while it autonomously manipulates the codebase.

**Key Engineering Features:**
* **Dual-Engine Modularity:** Intercepts and maps Google GenAI function schemas to local Ollama JSON specifications dynamically via a custom `schema_mapper`.
* **Context Propagation:** Sustains long-running ReAct loops by properly packaging and appending tool execution results (stdout/stderr) back into the LLM's context window.
* **Strict OS Sandboxing:** Employs absolute path resolution and common-path validation (`is_safe_path`) to trap the AI within designated workspace directories.
* **Safe Codebase Search:** Implements sub-process shell execution with strict timeout guillotines (`grep -r`) to allow the LLM to traverse large codebases without hanging the main thread.

## Motivation

Standard web-based LLM interfaces require tedious copy-pasting and lack crucial filesystem context. Developers waste time acting as the "middleman" between the AI and the terminal. 

I built this project to bridge that gap and bring the AI directly to the codebase. However, giving an LLM autonomous read/write/execute permissions is inherently dangerous. The core motivation was to engineer an AI that is both highly capable of manipulating real projects and mathematically constrained from touching anything outside its assigned sandbox. It is designed to be a transparent, rapid, and deterministic alternative to bloated commercial AI IDEs.

## Quick Start

The project relies on `uv` for deterministic, lightning-fast dependency resolution.

**Prerequisites:**
* Python 3.14+
* [uv package manager](https://github.com/astral-sh/uv)
* Google Gemini API Key (for Cloud execution)
* Ollama installed locally (for Local execution)

**Installation:**
1. Clone the repository and navigate into the project:
   ```bash
   git clone https://github.com/yourusername/ai-bot
   cd ai-bot
   ```

2. Sync the environment and install dependencies natively via `uv`:
   ```bash
   uv sync
   ```


3. Create a `.env` file in the root directory and add your API key:
   ```env
   GEMINI_API_KEY="your_api_key_here"

   ```



## Usage

The orchestrator (`main.py`) handles the user prompt, routing it to either the cloud or local engine based on the master toggle.

**Selecting the Engine:**
Inside `main.py`, modify the global toggle to choose your execution environment:

```python
# Set to True for Ollama (Local), False for Gemini (Cloud)
USE_LOCAL_MODEL = True 

```

**Executing an Autonomous Task:**
Simply run the orchestrator and pass your prompt. The agent is strictly locked to the `projects/` directory sandbox.

```bash
uv run main.py "Review the calculator project, find the bug in the division logic, write the fix, and run the tests.py file to verify."

```

**How it works under the hood:**

1. The agent reads the prompt and determines it needs to use `get_files_info`.
2. It lists the directory, then calls `get_file_content` on `calculator.py`.
3. It identifies the logic error and calls `write_file` to inject the corrected code.
4. It calls `run_python_file` on `tests.py`. If tests fail, it reads the traceback and loops back to step 3. If they pass, it exits gracefully.

## Contributing

The repository is structured to prioritize modularity, cleanly separating engines, tools, and sandboxed projects.

**Adding New Tools:**

1. Create a new python script inside the `functions/` directory (e.g., `git_commit.py`).
2. Define your python function and its associated GenAI `FunctionDeclaration` schema.
3. Import the schema into `main.py` and append it to the `available_functions` list. The `schema_mapper` will automatically ensure it works for both Gemini and Ollama!

If you build a new tool or optimize the ReAct context propagation, feel free to open a Pull Request. Please ensure your tools strictly utilize the `is_safe_path` validator from `config.py` to maintain sandbox integrity.
