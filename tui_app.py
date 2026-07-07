import uuid
import time
import ollama
import threading

from datetime import datetime
from textual import work
from textual.screen import ModalScreen
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Input, RichLog, ListItem, ListView, Label, Select, Switch, Button

from google.genai import types

# Importing local engines and the mapper utilities
from engines.ollama_engine import run_local_model

# Import core sandbox tools
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_code_outline import get_code_outline, schema_get_code_outline
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.patch_file import patch_file, schema_patch_file
from functions.run_python_file import run_python_file, schema_run_python_file
from functions.search_codebase import search_codebase, schema_search_codebase
from functions.git_manager import manage_git, schema_manage_git
from functions.delete_file import delete_file, schema_delete_file

# Importing the database connection drivers
from database import init_db, create_session, save_message, get_all_sessions, get_session_messages

# Packaging the definitions matching the original main.py
available_function_schemas = [
    schema_get_files_info,
    schema_get_code_outline,
    schema_get_file_content,
    schema_patch_file,
    schema_run_python_file,
    schema_search_codebase,
    schema_manage_git,
    schema_delete_file,
]

SYSTEM_PROMPT = """
You are Aegis, an advanced, autonomous AI coding agent.

You have access to a specific suite of tools to navigate, analyze, and modify the user's codebase. Always plan your actions step-by-step before executing them. 

Available Operations & Best Practices:
1. RECONNAISSANCE:
   - get_files_info: List files and directories to understand the project structure.
   - search_codebase: Find specific keywords, functions, or variables across the project.
   - get_code_outline: Use this FIRST on Python files to map out classes and function signatures without consuming massive amounts of tokens.
   - get_file_content: Read the exact text contents of a file. Use this after outlining if you need to see the specific internal logic.

2. FILE MODIFICATION:
   - patch_file: Your primary editing tool. Use this to perform surgical, exact-match string replacements for bug fixes or updates.
   - delete_file: Your primary deletion tool. Use this to remove precisely one file that you want to remove permanently from the working directory.
   
3. EXECUTION & SAFETY:
   - run_python_file: Execute scripts to test your code and view terminal output.
   - manage_git: Run native git commands (status, add, commit, restore) to track your changes or revert mistakes if a patch breaks the code.

CRITICAL RULES:
- All file paths you provide must be relative to the working directory. The root path is injected automatically for security.
- Prioritize token efficiency: Outline first, read second, patch third.
- If a patch fails due to a mismatch, do not guess. Re-read the file to get the exact spacing and indentation before trying again.
"""

class SessionListItem(ListItem):
    """Defining a custom ListItem that cleanly stores all of the associated database session ID"""
    def __init__(self, session_id: str, title: str) -> None:
        super().__init__()
        self.session_id = session_id

        # To add a clean label inside the item
        self.compose_add_child(Label(f"💬 {title}"))

class GateKeeperScreen(ModalScreen[bool]):
    """A blocking modal that requires explicit user approval for filesystem changes."""

    CSS = """
    GateKeeperScreen {
        align: center middle;
    }

    #dialog {
        padding: 1 2 ;
        width: 50;
        height: auto;
        border: thick red;
        background: $surface;
    }

    #dialog-buttons {
        layout: horizontal;
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 2;
    }
    """

    def __init__(self, tool_name: str, args: dict) -> None:
        super().__init__()
        self.tool_name = tool_name
        self.args = args
    
    def compose(self) -> ComposeResult:
        yield Container(
            Label("[bold red]⚠️SECURITY GATEKEEPER[/bold red]\n"),
            Label(f"Aegis is attempting to run: [bold yellow]{self.tool_name}[/bold yellow]"),
            Label(f"[dim]Target: {self.args.get('file_path', 'Unknown')}[/dim]"),
            Container(
                Button("Approve", variant="success", id="btn-approve"),
                Button("Deny", variant="error", id="btn-deny"),
                id="dialog-buttons",
            ),
            id="dialog"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-approve":
            self.dismiss(True)
        else:
            self.dismiss(False)

class AegisTUI(App):
    """A production grade TUI for Aegis Agent built using Textual"""

    # Custom CSS layout styling directly inside our application class
    CSS = """
        #app-grid {
            layout: grid;
            grid-size: 2;
            grid-columns: 1fr 3fr;
        }

        #sidebar {
            background: $surface;
            border-right: round cyan;
            padding: 1;
        }

        #sidebar-title {
            text-style: bold;
            margin-bottom: 1;
            color: $accent;
        }

        #chat-area {
            height: 1fr;
            border: solid $accent;
            background: $surface;
            margin-bottom: 1;
        }

        #user-input {
            dock: bottom;
        }

        #headless-toggle-container {
            height: auto;
            align: left middle;
            margin-bottom: 1;
            margin-top: 1;
        }

        #headless-label {
            margin-right: 1;
            padding-top: 1;
            color: $text-muted;
        }
    """

    def __init__(self) -> None:
        super().__init__()
        # Track our active session state in memory
        self.current_session_id = None

    def compose(self) -> ComposeResult:
        """Draws the visual structure of the layout"""
        yield Header(show_clock=True)

        with Container(id="app-grid"):
            # Live sidebar columns for different chat sessions
            with Vertical(id="sidebar"):
                # Engine Selection Dropdown
                yield Label("🧠 ENGINE SELECTION", id="engine-title")
                yield Select([], id="engine-select", prompt="Scanning local models...")

                # Headless Mode Toggle
                with Horizontal(id="headless-toggle-container"):
                    yield Label("Headless (Auto-Approve):", id="headless-label")
                    yield Switch(id="headless-toggle", value=False) # Default set to safe mode!

                yield Label("📂 CHAT SESSIONS", id="sidebar-title")
                yield ListView(id="session-list")
            
            # Right Main Working Panel
            with Vertical(id="chat-area"):
                yield RichLog(id="chat-log", highlight=True, markup=True, wrap=True)
                yield Input(placeholder="Ask Aegis to build or edit code...", id="user-input")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Runs setup initialization and populates the data layers from SQLite"""
        # 1. Making sure that the DB tables exists safely
        init_db()

        # 2. Refreshing the session dashboard sidebar
        self.refresh_sidebar()

        # 3. Model Discovery Logic
        engine_select = self.query_one("#engine-select", Select)
        try:
            local_models = ollama.list()
            # Mapping the models into a tuple format as required by the Select Widget: ("Label", "value")
            options = [(m['name'], m['name']) for m in local_models.get('models', [])]
            engine_select.set_options(options)

            # Default to the first found model if available
            if options:
                self.active_model = options[0][1]
                engine_select.value = self.active_model
            else:
                self.active_model = "gemma4" # Safety Fallback
        except Exception as e:
            engine_select.set_options([("Ollama Daemon Offline", "Offline")])
            self.active_model = "gemma4"
        
            log = self.query_one("#chat-log", RichLog)
            log.write(f"[bold red]Deamon Connection Error:[/bold red] {str(e)}")
        
        log = self.query_one("#chat-log", RichLog)
        log.write("[bold green]Aegis Agent Engine Initialzied Successfully.[/bold green]")
        log.write(f"Current Configuration: [cyan]{self.active_model.capitalize()} via local Daemon[/cyan].\n")
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """This starts up whenever a different model from the dropdown is picked"""
        if event.select.id == "engine-select" and event.value:
            self.active_model = event.value
            log = self.query_one("#chat-log", RichLog)
            log.write(f"\n[bold yellow]⚡ Engine hot-swapped to: {self.active_model}[/bold yellow]")

    def refresh_sidebar(self) -> None:
        """Queries SQLite and syncs the UI layout panel with true historical rows"""
        session_list = self.query_one("#session-list", ListView)
        session_list.clear()

        # ALways place a static 'New Session' action trigger at the absolute top
        session_list.append(SessionListItem(session_id="NEW", title="Start New Worspace"))

        # Pull real historical columns out of SQLite
        saved_sessions = get_all_sessions()
        for session in saved_sessions:
            session_list.append(SessionListItem(session_id=session["id"], title=session["title"]))
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Gracefully swaps the chat session to the one clicked within the sidebar"""
        selected_item = event.item
        if not isinstance(selected_item, SessionListItem):
            return
        
        log = self.query_one("#chat-log", RichLog)
        log.clear()

        if selected_item.session_id == "NEW":
            self.current_session_id = None
            log.write("[bold green]✨ Started a clean unprimed workspace session.[/bold green]")
            return
        
        # Swapping active session pointers to fetch historical messages
        self.current_session_id = selected_item.session_id
        log.write(f"[bold cyan]🔁 Loaded active history context for Session ID: {self.current_session_id}[/bold cyan]\n")

        historical_messages = get_session_messages(self.current_session_id)
        for msg in historical_messages:
            role_label = "[bold blue]👤 User:[/bold blue]" if msg["role"] == "user" else "[bold magenta]🤖 Aegis:[/bold magenta]"
            log.write(f"{role_label} {msg['content']}")
            if msg["role"] == "assistant" and (msg["prompt_tokens"] > 0 or msg["completion_tokens"] > 0):
                log.write(f"[dim gray]📥 {msg['prompt_tokens']} tokens | 📤 {msg['completion_tokens']} tokens[/dim gray]\n")
    
    def on_input_submitted(self, event=Input.Submitted) -> None:
        """Captures the input string and provisions the rows inside SQLite, and fires execution traces"""
        user_text = event.value.strip()
        if not user_text:
            return
        
        log = self.query_one("#chat-log", RichLog)
        input_widget = self.query_one("#user-input", Input)

        # Lazily initializing a new tracking instance by default
        if self.current_session_id is None:
            self.current_session_id = str(uuid.uuid4())[:8] # Simple short tracking key

            # Titling the session using a clean truncated version of the first prompt
            session_title = user_text if len(user_text) <= 25 else f"{user_text[:22]}..."
            create_session(self.current_session_id, session_title)
            self.refresh_sidebar()
        
        # 1. Commit user text row securely into the local SQLite messages timeline
        save_message(self.current_session_id, role="user", content=user_text)
        log.write(f"\n[bold blue]👤 User:[/bold blue] {user_text}")
        
        # 2. Locking the text box to a clean slate
        input_widget.value = ""

        # 3. Firing off the background worker thread
        self.run_agent_loop(user_text)
    
    @work(thread=True)
    def run_agent_loop(self, user_prompt: str) -> None:
        """Asynchronous execution progressing the ReAct model decisions without UI freezes"""
        log = self.query_one("#chat-log", RichLog)
        working_dir = "projects/calculator"

        # Hydrate message history stream from database
        db_history = get_session_messages(self.current_session_id)
        messages = []
        for row in db_history:
            messages.append(
                types.Content(role=row['role'], parts=[types.Part(text=row["content"])])
            )
        
        start_time = time.time()

        # Stepping through the loop upto 20 times to map the code development
        for iteration in range(20):
            log.write(f"[italic gray]⚙️ Agent running loop iteration {iteration + 1}...[/italic gray]")

            try:
                # Direct lookup payload to Ollama Daemon
                raw_response = run_local_model(messages, available_function_schemas, SYSTEM_PROMPT, model_name=self.active_model)

                # Extracting the telemetry statistics integers natively
                prompt_tokens = raw_response.get('prompt_eval_count', 0)
                completion_tokens = raw_response.get('eval_count', 0)

                # Standardize structures matching your main.py layout patterns
                class MockResponse: pass
                class MockCall: pass
                response = MockResponse()
                response.text = raw_response['message'].get('content', "")
                response.function_calls = []

                if 'tool_calls' in raw_response['message']:
                    for tc in raw_response['message']['tool_calls']:
                        mock_call = MockCall()
                        mock_call.name = tc['function']['name']
                        mock_call.args = tc['function']['arguments']
                        response.function_calls.append(mock_call)
            
            except Exception as engine_err:
                log.write(f"[bold red]❌ Model Engine Configuration Error: {engine_err}[/bold red]")
                return
            
            # Tool Execution Check Block
            if response.function_calls:
                for call in response.function_calls:
                    log.write(f"[bold yellow]🛠️ Invoking Tool Call: {call.name}({call.args})[/bold yellow]")

                    try:
                        function_result = None
                        name = call.name
                        args = call.args

                        # Match logic mirroring main.py switch case structures
                        if name == "patch_file":
                            # Checking if Headless Mode is Active
                            is_headless = self.query_one("#headless-toggle", Switch).value

                            if is_headless:
                                # Bypassing the Gatekeeper completely
                                log.write("[bold orange]⚠️ Headless Mode Active: Auto-Approving file patch...[/bold orange]")
                                function_result = patch_file(
                                    working_directory=working_dir,
                                    file_path=args["file_path"],
                                    search_block=args["search_block"],
                                    replace_block=args["replace_block"],
                                )
                            else:
                                # Standard "Human-in-the-loop" Gatekeeping Mode
                                log.write(f"[bold orange]⏸️ Halting Execution! Waiting for User Authorization on {name}...[/bold orange]")

                                approval_event = threading.event()
                                user_approved=False

                                def gatekeeper_callback(result: bool):
                                    nonlocal user_approved
                                    user_approved = result
                                    approval_event.set()
                                
                                self.call_from_thread(self.push_screen, GateKeeperScreen(name, args), gatekeeper_callback)
                                approval_event.wait()

                                if not user_approved:
                                    function_result = "Error: User strictly denied permission to execute this filesystem patch"
                                    log.write("[bold red]❌ Execution Denied by User[/bold red]")
                                else:
                                    log.write("[bold green]✅ Authorization Granted. Patching file...[/bold green]")
                                    function_result = patch_file(
                                        working_directory=working_dir,
                                        file_path=args["file_path"],
                                        search_block=args['search_block'],
                                        replace_block=['replace_block']
                                    )

                        elif name == "get_code_outline":
                            function_result = get_code_outline(
                                working_directory=working_dir,
                                file_path=args["file_path"],
                            )
                        elif name == "get_file_content":
                            function_result = get_file_content(
                                working_directory=working_dir,
                                file_path=args["file_path"],
                            )
                        elif name == "get_files_info":
                            function_result = get_files_info(
                                working_directory=working_dir,
                                directory=args.get('directory', ".")
                            )
                        elif name == "run_python_file":
                            # Checking if the headless mode is active
                            is_headless = self.query_one("#headless-toggle", Switch).value

                            if is_headless:
                                log.write("[bold orange]⚠️ Headless Mode Active: Auto-Approving code execution...[/bold orange]")
                                function_result = run_python_file(
                                    working_directory=working_dir,
                                    file_path=args["file_path"],
                                )
                            else:
                                # Standard "Human-in-the-loop" Gatekeeping Mode
                                log.write(f"[bold orange]⏸️ Halting Execution: Waiting for User AUthorization on {name}...[/bold orange]")

                                approval_event = threading.Event()
                                user_approved = False

                                def gatekeeper_callback(result: bool):
                                    nonlocal user_approved
                                    user_approved = result
                                    approval_event.set()
                                
                                self.call_from_thread(self.push_screen, GateKeeperScreen(name, args), gatekeeper_callback)
                                approval_event.wait()

                                if not user_approved:
                                    function_result = "Error: User strictly denied permission to execute this script."
                                    log.write("[bold red]❌ Execution Denied by User[/bold red]")
                                else:
                                    log.write("[bold green]✅ Authorization Granted. Executing script...[/bold green]")
                                    function_result = run_python_file(
                                        working_directory=working_dir,
                                        file_path=args["file_path"],
                                    )

                        elif name == "search_codebase":
                            function_result = search_codebase(
                                working_directory=working_dir,
                                keyword=args.get("keyword", str(args))
                            )
                        elif name == "manage_git":
                            function_result = manage_git(
                                working_directory=working_dir,
                                git_command=args.get("command", str(args))
                            )
                        elif name == "delete_file":
                            function_result = delete_file(
                                working_directory=working_dir,
                                file_path=args.get("relative_file_path", str(args))
                            )
                        else:
                            function_result = f"Error: Tool '{name}' does not exist inside active environment scopes."
                        
                        log.write(f"[dim green]✅ Execution Complete: {name}[/dim green]")
                    
                    except Exception as tool_err:
                        function_result = f"Error: Executing Function: {tool_err}"
                        log.write(f"[bold red]❌ Tool execution runtime exception : {tool_err}[/bold red]")
                    
                    # Standardizing 'appending' for ReAct tracing loop
                    messages.append(
                        types.Content(role="assistant", parts=[types.Part(text=f"Action Executed:{name} with arguments {args}")])
                    )
                    
                    messages.append(
                        types.Content(role="user", parts=[types.Part(text=f"Tool Result: {str(function_result)}")])
                    )
            
            else:
                # Terminal text generated successfully
                if response.text:
                    elapsed_time = time.time() - start_time

                    # 1. Writing the content block to the screen layout pane
                    log.write(f"\n[bold magenta]🤖 Aegis:[/bold magenta] {response.text}")

                    # 2. Rendering layout performance telemetry line layout directly below it
                    log.write(f"[dim gray]⏱️ {elapsed_time:.1f}s | 📥 {prompt_tokens} tokens | 📤 {completion_tokens} tokens[/dim gray]")

                    # 3. Committing text responses along with true statistics columns to disks records
                    save_message(
                        self.current_session_id,
                        role="assistant",
                        content=response.text,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                    )
                    break

if __name__=="__main__":
    app = AegisTUI()
    app.run()