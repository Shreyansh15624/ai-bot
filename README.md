# AegisAgent: The Sandboxed Autonomous AI Coder (TUI Workspace)

## Description

AegisAgent is a modular, terminal-native AI development workspace engineered to manipulate, execute, and debug code autonomously within a secure environment. Instead of relying on rigid, one-shot code generation or tedious web interface copy-pasting, Aegis operates via an interactive **Text User Interface (TUI)** built on top of a dynamic **ReAct (Reasoning and Acting)** feedback loop. The agent plans its actions step-by-step, invokes real filesystem and system tools, reads execution outputs or traceback errors, and self-corrects until its objective is successfully achieved.

The platform abstracts cloud-based reasoning (Google Gemini) and local, privacy-first execution (Ollama) into a single unified workspace. To protect the host machine from autonomous execution risks, all filesystem actions are bound by a rigid path-resolution sandbox and monitored by an interactive, real-time security gatekeeper.

---
> ### 🚧 Active Development & Pre-Alpha Notice
> AegisAgent is currently undergoing active, rapid development and architectural refinement. While the core asynchronous ReAct engine, SQLite persistence layer, and basic Textual TUI layouts are functional, the codebase is in a pre-alpha state. Expect frequent breaking changes, UI polish updates, and tool schema evolutions. Features and configuration steps are being optimized daily to streamline collaborative local environments.
---

## Core Architectural Features

### 1. Interactive Textual TUI Workspace

Built using the `Textual` framework, the interface transforms the terminal into a full-fledged IDE dashboard:

* **Dynamic Sidebar:** Features hot-swappable local model discovery via a live Ollama daemon scan, an industrial-grade workspace history loader, and runtime mode switches.
* **Rich Operational Telemetry:** The main console employs a dedicated `RichLog` that prints step-by-step execution traces, exact tool argument telemetry, and millisecond-accurate model generation benchmarks.

### 2. Dual-Engine Schema Mapping

Aegis bridges cloud-scale reasoning and local inference out of the box. Through a custom `schema_mapper` engine, Google GenAI `FunctionDeclaration` structures are dynamically compiled down into standard local Ollama JSON tool specifications at runtime, allowing the exact same tool suite to work seamlessly across local or remote backends.

### 3. Human-in-the-Loop & Headless Security

To mitigate the risks of autonomous AI filesystem execution, Aegis implements two distinct security postures:

* **Gatekeeper Mode (Default):** Before dangerous system tools (like `patch_file` or `run_python_file`) can execute, the TUI halts the main thread and throws a modal `GateKeeperScreen` requiring explicit user authorization via an asset-safe confirmation prompt.

* **Headless Mode:** A persistent toggle switch that allows advanced developers to bypass the gatekeeper, granting the agent full, unprompted autonomy for accelerated debugging sprints.

### 4. SQLite Session Persistence

Every conversational turn, tool invocation, and token consumption profile is written to a local `aegis_memory.db` file driven by a structured SQLite indexing layer. This ensures that long-running debugging context is never lost across machine restarts.

---

## Project Topology

```bash
.
├── aegis_memory.db            # SQLite persistent session database
├── database.py                # Database drivers, indexing, and logging routines
├── pyproject.toml             # uv package declaration and exact dependencies
├── uv.lock                    # Deterministic lockfile
├── tui_app.py                 # Core TUI Entrypoint (Textual Application)
├── Makefile                   # Automation scripts for sandboxed environments
├── engines/                   # Inference coordination layer
│   ├── __init__.py
│   ├── gemini_engine.py       # Cloud engine interface
│   ├── ollama_engine.py       # Local daemon manager
│   └── schema_mapper.py       # Dynamic tool schema conversion library
├── functions/                 # Sandboxed tool suite (ReAct capabilities)
│   ├── __init__.py
│   ├── config.py              # Path resolution and is_safe_path bounds checking
│   ├── delete_file.py         # Precision filesystem removal tool
│   ├── get_code_outline.py    # High-efficiency Python AST outline compiler
│   ├── get_file_content.py    # Targeted file reader
│   ├── get_files_info.py      # Directory topology scanner
│   ├── git_manager.py         # Subprocess Git state tracking interface
│   ├── patch_file.py          # Surgical exact-match string block editing utility
│   ├── run_python_file.py     # Subprocess runner with execution trace trapping
│   └── search_codebase.py     # Grep-driven high-speed codebase searching tool
├── templates/                 # Pristine testing environments
│   └── calculator/
└── projects/                  # Active runtime sandboxes (AI Workspace Target)
    └── calculator/

```

---

## Quick Start

Aegis relies on the `uv` package manager for deterministic environment resolution.

### Prerequisites

* Python `3.14+`
* [uv package manager](https://github.com/astral-sh/uv)
* Ollama Daemon running locally (for local models)
* Google Gemini API Key (for cloud models)

### Setup & Onboarding

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Shreyansh15624/aegis-agent.git
   cd aegis-agent
   ```


2. **Establish the Environment & Dependencies:**
Utilize `uv` to instantly compile the virtual environment and sync the exact dependency graph:
   ```bash
   uv sync
   ```


3. **Configure Environment Secrets:**
Create a `.env` file in the project root directory:
   ```env
   GEMINI_API_KEY="your_production_api_key_here"
   ```


4. **Initialize the Sandbox Infrastructure:**
Run the setup script via the `Makefile` to securely clear out old runs and provision a pristine workspace:
   ```bash
   make reset
   ```


5. **Boot the Workspace TUI:**
Execute the core application context directly through `uv`:
   ```bash
   uv run tui_app.py
   ```



---

## Technical Workflows

### Operating within the ReAct Loop

When you enter a task in the input field (e.g., *"Find the bug in compound_interest.py, fix it, and verify by running tests"*), Aegis executes the following sequence:

```md
  [ User Prompt Entered ] 
             │
             ▼
    ┌─────────────────┐
    │  Reasoning Loop │◄────────────────────────┐
    └────────┬────────┘                         │
             │ (Determines Action Needed)       │
             ▼                                  │
    ┌─────────────────┐                         │
    │ Tool Invocation │                         │
    └────────┬────────┘                         │
             │                                  │
   [ Headless Mode Active? ]                    │
      ├── No  ──► [ Show Gatekeeper Modal ]     │
      │                  │ (User Approves)      │
      │                  ▼                      │
      └── Yes ──► [ Safe Path Evaluation ]      │
                         │                      │
                         ▼                      │
             ┌───────────────────────┐          │
             │   Execute Tool in     │          │
             │  projects/ Sandbox    │          │
             └───────────┬───────────┘          │
                         │                      │
                         ▼                      │
             [ Trap stdout / stderr ] ──────────┘
                         │ (Loop completes/Success)
                         ▼
             [ Render Final Response ]

```

### Developing & Injecting New Tools

The tool suite is heavily decoupled, making it incredibly simple to write extensions:

1. **Write the Core Routine:** Create a standalone Python file within the `functions/` directory. Ensure it imports and implements the core security path verification checks from `functions/config.py`:
```python
# Example snippet inside a new file: functions/create_directory.py
from functions.config import is_safe_path

def create_directory(working_directory: str, folder_name: str):
    # Always validate that the action is mathematically locked inside the sandbox
    # ... your code here ...

```


2. **Define the Schema:** Author an explicit Google GenAI `FunctionDeclaration` dictionary matching the parameters of your routine.
3. **Register the Capability:** Import both your function and its declaration schema into `tui_app.py`, then append the declaration object directly into the `available_function_schemas` list. The engine's mapping layer will handle the rest.