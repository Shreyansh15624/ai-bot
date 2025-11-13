# ai-bot 🤖

[![boot.dev Project](https://img.shields.io/badge/Project-Boot.dev-blueviolet)](https://boot.dev)

This repository contains a Python project for an AI agent, built by following the "Building an AI Agent with Python" guided project on the Boot.dev platform.

## ✨ Features

From the project structure, it looks like this agent includes:

* **Extensible Functions:** The ability to add custom tools and functions (located in the `/functions` directory).
* **Calculator Tool:** A built-in calculator for handling mathematical queries (located in the `/calculator` directory).
* **Core Agent Logic:** A central `main.py` that likely orchestrates the agent's behavior.

## 🛠️ Tech Stack

* **Language:** Python
* **Package Management:** uv
* **Testing:** pytest

## 🚀 Getting Started

Here's how to get a local copy up and running.

### Prerequisites

Before you begin, make sure you have the following installed:

* **Python:** This project uses `python3.14`.
* **uv:** This project uses `uv` for package management. You can install it with:
    ```sh
    pip install uv
    ```
* **API Keys:** You will likely need an API key from an AI provider (like OpenAI, Anthropic, or Google).
    * `[...List the API keys needed, e.g., GOOGLE_GENAI_API_KEY...]`

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/Shreyansh15624/ai-bot.git](https://github.com/Shreyansh15624/ai-bot.git)
    cd ai-bot
    ```

2.  **Create a virtual environment:**
    ```sh
    # Using uv
    uv venv
    ```

3.  **Activate the virtual environment:**
    ```sh
    # On macOS/Linux
    source .venv/bin/activate
    
    # On Windows
    .venv\Scripts\activate
    ```

4.  **Install dependencies:**
    ```sh
    # Using uv (it reads from pyproject.toml)
    uv pip install -r requirements.txt 
    # OR if you have dependencies in pyproject.toml under [project.dependencies]
    uv pip install .
    ```
    *(Note: You'll need to confirm the exact install command based on your `pyproject.toml` setup. If you just have a `requirements.txt`, use that.)*

## 🔧 Configuration

The agent needs to be configured with your API keys.

1.  Create a `.env` file in the root directory:
    ```sh
    touch .env # use a different command for windows
    ```

2.  Add your API keys and any other environment variables to the `.env` file:
    ```
    # Example
    GOOGLE_GENAI_API_KEY="sk-..."
    [...ANY_OTHER_VARIABLES...]
    ```
    *(Remember to add `.env` to your `.gitignore` file if it's not already there!)*

## Usage

Once installed and configured, you can run the bot from the command line.

```sh
# Example of how to run your bot
python main.py "[...Your prompt for the bot...]"

# Example for getting more details regarding tokenization
python main.py "[...Your prompt for the bot...]" --verbose
```