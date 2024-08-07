# Cursor Chat Export

This project provides a command-line interface (CLI) tool to discover and export AI chat data from [Cursor](https://cursor.sh). The tool is implemented in `chat.py` and leverages utility classes for querying the database, formatting the chat data, and saving it to files.

Cursor's chat history is stored in `sqlite3` databases using `state.vscdb` files. One such file is for one workspace. All the chats for a workspace are saved here in so called *tabs*, one tab means a single chat.

Also see [this](https://forum.cursor.com/t/guide-5-steps-exporting-chats-prompts-from-cursor/2825) forum post on this topic.

## Features

- **Discover Chats**: Discover all chats from all workspaces and print a few lines of dialogue so one can identify which is the workspace (or chat) one is searching for. It's also possible to filter by text.
- **Export Chats**: Export chats for the most recent (or a specific) workspace to Markdown files or print it to the command line.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/somogyijanos/cursor-chat-export.git
    cd cursor-chat-export
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

First, find, where the `state.vscdb` files are located on your computer. Confirm that corresponding to your system, the right path is set in the [config.yml](./config.yml) file. Update it if not set correctly.

Both the `discover` and `export` commands will work with this path by default, but you can also provide a custom path any time.

---

### Discover Chats
```sh
# Help on usage
./chat.py discover --help

# Discover all chats from all workspaces
./chat.py discover

# Apply text filter
./chat.py discover --search-text "matplotlib"

# Discover all chats from all workspaces at a custom path
./chat.py discover "/path/to/workspaces"
```

---

### Export Chats
See `./chat.py export --help` for general help. Examples:
```sh
# Help on usage
./chat.py export --help

# Print all chats of the most recent workspace to the command line
./chat.py export

# Export all chats of the most recent workspace as Markdown
./chat.py export --output-dir "/path/to/output"

# Export only the latest chat of the most recent workspace
./chat.py export --latest-tab --output-dir "/path/to/output"

# Export all chats of a specifc workspace
./chat.py export --output-dir "/path/to/output" "/path/to/workspaces/workspace-dir/state.vscdb"
```
