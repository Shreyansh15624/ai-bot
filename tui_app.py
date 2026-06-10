import uuid
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Input, RichLog, ListItem, ListView, Label

from database import init_db, create_session, save_message, get_all_sessions, get_session_messages

class SessionListItem(ListItem):
    """Defining a custom ListItem that cleanly stores all of the associated database session ID"""
    def __init__(self, session_id: str, title: str) -> None:
        super().__init__()
        self.session_id = session_id

        # To add a clean label inside the item
        self.compose_add_child(Label(f"💬 {title}"))


class AegisTUI(App):
    """A production grade TUI for Aegis Agent built using Textual"""

    # Custom CSS layout styling directly inside our application class
    CSS = """
        #app-grid {
            layout: grid;
            grid-size: 2;
            grid-columns: 1fr 3fr;
        }

        #side-bar {
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
                yield Label("CHAT SESSIONS", id="sidebar-title")
                yield ListView(id="session-list")
            
            # Right Main Working Panel
            with Vertical(id="chat-area"):
                yield RichLog(id="chat-log", highlight=True, markup=True)
                yield Input(placeholder="Ask Aegis to build or edit code...", id="user-input")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Runs setup initialization and populates the data layers from SQLite"""
        # 1. Making sure that the DB tables exists safely
        init_db()

        # 2. Refreshing the session dashboard sidebar
        self.refresh_sidebar()

        # 3. Bootstraping the initial system workspace state
        log = self.query_one("#chat-log", RichLog)
        log.write("[bold green]Aegis Agent Engine Initialized Successfully.[/bold green]")
        log.write("Current Configuration: [cyan]Gemma 4 via local Daemon[/cyan].\n")
        log.write("Select a past session or typing a prompt to spin up a new workspace context.")
    
    def refresh_sidebar(self) -> None:
        """Queries SQLite and syncs the UI layout panel with true historical rows"""
        session_list = self.query_one("#session-list", ListView)
        session_list.clear()

        # ALways place a static 'New Session' action trigger at the absolute top
        session_list.append(SessionListItem(session_id="NEW", title="Start New Worspace"))

        # Pull real historical columns out of SQLite
        saved_sessions = get_all_sessions()
        for session in saved_sessions:
            session_list.append(
                SessionListItem(session_id=session["id"], title=session["title"])
            )
    
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
            log.write("Your next prompt will generate a brand new histocial tracking session.")
            return
        
        # Swapping active session pointers to fetch historical messages
        self.current_session_id = selected_item.session_id
        log.write(f"[bold cyan]🔁 Loaded active history context for Session ID: {self.current_session_id}[/bold cyan]\n")

        historical_messages = get_session_messages(self.current_session_id)
        for msg in historical_messages:
            role_label = "[bold blue]👤 User:[/bold blue]" if msg["role"] == "user" else "[bold magenta]🤖 Aegis:[/bold magenta]"
            log.write(f"{role_label} {msg["content"]}")
    
    def on_input_submitted(self, event=Input.Submitted) -> None:
        """Captures the input string and provisions the rows inside SQLite, and fires execution traces"""
        user_text = event.value.strip()
        if not user_text:
            return
        
        log = self.query_one("#chat-log", RichLog)

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
        self.query_one("#user-input", Input).value = ""

        # 2. Mock Agent Loop Action (will be swapped with the real one later)
        agent_reply_mock = f"Simulated local execution tracing complete for context window tracking under session checkpoint: {self.current_session_id}."

        # 3. Commit agent response row securely into the local SQLite messages timeline
        save_message(self.current_session_id, role="assistant", content=agent_reply_mock)
        log.write(f"[bold magenta]🤖 Aegis:[/bold magenta] {agent_reply_mock}")

if __name__=="__main__":
    app = AegisTUI()
    app.run()