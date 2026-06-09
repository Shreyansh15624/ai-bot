from httpx import __name
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Input, RichLog, ListItem, ListView, Label

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

    def compose(self) -> ComposeResult:
        """Draws the visual structure of the layout"""
        yield Header(show_clock=True)

        with Container(id="app-grid"):
            # Live sidebar columns for different chat sessions
            with Vertical(id="sidebar"):
                yield Label("CHAT SESSIONS", id="sidebar-title")
                yield ListView(
                    ListItem(Label("New Session Workspace")),
                    ListItem(Label("Fix Calculator Logic")),
                    ListItem(Label("Refactor Runtime Tests")),
                    id="session-list",
                )
            
            # Right Main Working Panel
            with Vertical(id="chat-area"):
                yield RichLog(id="chat-log", highlight=True, markup=True)
                yield Input(placeholder="Ask Aegis to build or edit code...", id="user-input")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Runs initialization setup scripts when the interface loads on screen"""
        log = self.query_one("#chat-log", RichLog)
        log.write("[bold green]Aegis Agent Engine Initialized Successfully.[/bold green]")
        log.write("Current COnfiguration: [cyan]Gemma 4 Local Ollama Daemon[/cyan].\n")
        log.write("Type your instructions down in the text box below to start a test cycle.")
    
    def on_input_submitted(self, event=Input.Submitted) -> None:
        """Handles what happens when the user hits enter inside the input text field box"""
        user_text = event.value.strip()
        if not user_text:
            return
        
        log = self.query_one("#chat-log", RichLog)

        # Logging the user text instantly in the screen console
        log.write(f"\n[bold blue]👤 User:[/bold blue] {user_text}")

        # Resetting input box for a clean slate
        self.query_one("#user-input", Input).value = ""

        # Dummy system test feedback loop before the Integration
        log.write("[italic system]⚙️ Agent running local calucaltions...[/italic system]")

if __name__=="__main__":
    app = AegisTUI()
    app.run()