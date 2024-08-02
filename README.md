# Cursor Chat Export

This project provides a command-line interface (CLI) tool to discover and export AI chat data from [Cursor](https://cursor.sh). The tool is implemented in `chat.py` and leverages utility classes for querying the database, formatting the chat data, and saving it to files.

Cursor's chat history is stored in `sqlite3` databases using `state.vscdb` files. One such file is for one workspace. All the chats for a workspace are saved here in so called *tabs*, one tab means a single chat.

Also see [this](https://forum.cursor.com/t/guide-5-steps-exporting-chats-prompts-from-cursor/2825) forum post on this topic.

## Features

- **Discover Chats**: Discover all `state.vscdb` files in a directory and print a few lines of dialogue so one can identify which is the workspace (chat) one is searching for. It's also possible to filter by text.
- **Export Chats**: Export chats data for a certain workspace to Markdown files or print it to the command line.

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

Find, where the `state.vscdb` is located in your computer. The table below may help:

| OS               | Path                                                      |
|------------------|-----------------------------------------------------------|
| Windows          | `%APPDATA%\Cursor\User\workspaceStorage`                  |
| macOS            | `/Users/YOUR_USERNAME/Library/Application Support/Cursor/User/workspaceStorage` |
| Linux            | `/home/YOUR_USERNAME/.config/Cursor/User/workspaceStorage` |

### Discover Chats of all Workspaces
```sh
python3 chat.py discover --search-text "matplotlib"
```

### Export Chats of a Workspace
```sh
python3 chat.py export --output-dir output "/Users/myuser/Library/Application Support/Cursor/User/workspaceStorage/b989572f2e2186b48b808da2da437416/state.vscdb"
```

If no directory is provided, the tool will automatically use the default Cursor workspace storage directory for your OS.

### Auto-detect and Export Workspace Chats
```sh
python3 chat.py export --output-dir output
```

If no database path is provided, the tool will automatically use the most recent workspace.

You can use the `--latest-tab` flag to export only the most recent tab:

```sh
python3 chat.py export --output-dir output --latest-tab
```

Examples:

```sh
# Export all tabs from a specific workspace
python3 chat.py export --output-dir output "/Users/myuser/Library/Application Support/Cursor/User/workspaceStorage/b989572f2e2186b48b808da2da437416/state.vscdb"

# Export the latest tab from a specific workspace
python3 chat.py export --output-dir output --latest-tab "/Users/myuser/Library/Application Support/Cursor/User/workspaceStorage/b989572f2e2186b48b808da2da437416/state.vscdb"

# Export all tabs from the most recent workspace
python3 chat.py export --output-dir output

# Export the latest tab from the most recent workspace
python3 chat.py export --output-dir output --latest-tab
```

These commands will automatically detect the appropriate directory for your OS when needed, find the latest workspace if no path is provided, and export the chats to the specified output directory according to the chosen options.
