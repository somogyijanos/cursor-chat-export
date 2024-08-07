#!/usr/bin/env python

import os
import sys
import typer
from src.vscdb import VSCDBQuery
from src.export import ChatExporter, MarkdownChatFormatter, MarkdownFileSaver
from rich.console import Console
from rich.markdown import Markdown
from loguru import logger
import json
import yaml
import platform
from pathlib import Path
import yaml

logger.remove()
logger.add(sys.stderr, level="DEBUG")

app = typer.Typer()
console = Console()

# Add this new function to get the config file path
def get_config_path(is_system_install: bool, provided_path: str) -> str:
    if is_system_install:
        return "/usr/lib/cursor-chat-export/config.yml"
    elif provided_path != "config.yml":
        return provided_path
    else:
        return "config.yml"

@app.command()
def export(
    db_path: str = typer.Argument(None, help="The path to the SQLite database file. If not provided, the latest workspace will be used."),
    output_dir: str = typer.Option(None, help="The directory where the output markdown files will be saved. If not provided, prints to command line."),
    latest_tab: bool = typer.Option(False, "--latest-tab", help="Export only the latest tab. If not set, all tabs will be exported."),
    system_install: bool = typer.Option(False, "--system-install", help="Indicates if this is a system-wide installation."),
    config_path: str = typer.Option(None, "--config-path", help="Path to the config.yml file.")
):
    """
    Export chat data from the database to markdown files or print it to the command line.
    """
    if not db_path:
        db_path = get_latest_workspace_db_path()

    image_dir = None
    # logger.debug(f"Command line args: {sys.argv}")  # Log all command line arguments to see what is being passed
    # logger.debug(f"System install flag: {system_install}")
    # logger.debug(f"Provided config path: {config_path}")

    config_path = get_config_path(system_install, config_path)
    # logger.debug(f"Final config path: {config_path}")

    try:
        # Query the AI chat data from the database
        db_query = VSCDBQuery(db_path, config_path)
        chat_data = db_query.query_aichat_data()

        if "error" in chat_data:
            error_message = f"Error querying chat data: {chat_data['error']}"
            logger.error(error_message)
            raise typer.Exit(code=1)

        # Convert the chat data from JSON string to dictionary
        chat_data_dict = json.loads(chat_data[0])

        if latest_tab:
            # Get the latest tab by timestamp
            latest_tab = max(chat_data_dict['tabs'], key=lambda tab: tab.get('timestamp', 0))
            chat_data_dict['tabs'] = [latest_tab]

        # Check if there are any images in the chat data
        has_images = any('image' in bubble for tab in chat_data_dict['tabs'] for bubble in tab.get('bubbles', []))

        if has_images and output_dir:
            image_dir = os.path.join(output_dir, 'images')

        # Format the chat data
        formatter = MarkdownChatFormatter()
        formatted_chats = formatter.format(chat_data_dict, image_dir)

        if output_dir:
            # Save the chat data
            saver = MarkdownFileSaver()
            exporter = ChatExporter(formatter, saver)
            exporter.export(chat_data_dict, output_dir, image_dir)
            success_message = f"Chat data has been successfully exported to {output_dir}"
            logger.info(success_message)
        else:
            # Print the chat data to the command line using markdown
            for formatted_data in formatted_chats:
                console.print(Markdown(formatted_data))
            logger.info("Chat data has been successfully printed to the command line")
    except KeyError as e:
        error_message = f"KeyError: {e}. The chat data structure is not as expected. Please check the database content."
        logger.error(error_message)
        raise typer.Exit(code=1)
    except json.JSONDecodeError as e:
        error_message = f"JSON decode error: {e}"
        logger.error(error_message)
        raise typer.Exit(code=1)
    except FileNotFoundError as e:
        error_message = f"File not found: {e}"
        logger.error(error_message)
        raise typer.Exit(code=1)
    except Exception as e:
        error_message = f"Failed to export chat data: {e}"
        logger.error(error_message)
        raise typer.Exit(code=1)

def get_cursor_workspace_path() -> Path:
    config_path = Path("config.yml")
    logger.debug(f"Looking for configuration file at: {config_path}")
    
    if not config_path.exists():
        error_message = f"Configuration file not found: {config_path}"
        logger.error(error_message)
        raise FileNotFoundError(error_message)

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    logger.debug("Configuration file loaded successfully")

    system = platform.system()
    logger.debug(f"Detected operating system: {system}")

    if system not in config["default_vscdb_dir_paths"]:
        error_message = f"Unsupported operating system: {system}"
        logger.error(error_message)
        raise ValueError(error_message)

    base_path = Path(os.path.expandvars(config["default_vscdb_dir_paths"][system])).expanduser()
    logger.debug(f"Resolved base path: {base_path}")

    if not base_path.exists():
        error_message = f"Cursor workspace storage directory not found: {base_path}"
        logger.error(error_message)
        raise FileNotFoundError(error_message)

    logger.info(f"Cursor workspace storage directory found: {base_path}")
    return base_path

def get_latest_workspace_db_path() -> str:
    base_path = get_cursor_workspace_path()
    workspace_folder = max(base_path.glob("*"), key=os.path.getmtime)
    db_path = workspace_folder / "state.vscdb"
    
    if not db_path.exists():
        raise FileNotFoundError(f"state.vscdb not found in {workspace_folder}")

    return str(db_path)

@app.command()
def discover(
    directory: str = typer.Argument(None, help="The directory to search for state.vscdb files. If not provided, the default Cursor workspace storage directory will be used."),
    limit: int = typer.Option(None, help="The maximum number of state.vscdb files to process. Defaults to 10 if search_text is not provided, else -1."),
    search_text: str = typer.Option(None, help="The text to search for in the chat history.")
):
    """
    Discover all state.vscdb files in a directory and its subdirectories, and print a few lines of dialogue.
    """
    if not directory:
        directory = str(get_cursor_workspace_path())
    
    if limit is None:
        limit = -1 if search_text else 10

    try:
        state_files = []
        for root, _, files in os.walk(directory):
            if 'state.vscdb' in files:
                db_path = os.path.join(root, 'state.vscdb')
                state_files.append((db_path, os.path.getmtime(db_path)))

        # Sort files by modification time (newest first)
        state_files.sort(key=lambda x: x[1], reverse=True)

        # Only process the newest files up to the specified limit, unless limit is -1
        if limit != -1:
            state_files = state_files[:limit]

        results = []

        # Process the files
        for db_path, _ in state_files:
            db_query = VSCDBQuery(db_path)
            chat_data = db_query.query_aichat_data()

            if "error" in chat_data:
                error_message = f"Error querying chat data from {db_path}: {chat_data['error']}"
                logger.error(error_message)
            elif not chat_data:
                logger.debug(f"No chat data found in {db_path}")
            else:
                chat_data_dict = json.loads(chat_data[0])
                formatter = MarkdownChatFormatter()
                formatted_chats = formatter.format(chat_data_dict, image_dir=None)
                
                if search_text:
                    # Filter the formatted data to include only lines containing the search text
                    for formatted_data in formatted_chats:
                        filtered_lines = [line for line in formatted_data.splitlines() if search_text.lower() in line.lower()]
                        if filtered_lines:
                            results.append((db_path, "\n".join(formatted_data.splitlines()[:10]) + "\n..."))
                    if not filtered_lines:
                        logger.debug(f"No chat entries containing '{search_text}' found in {db_path}")
                else:
                    # Collect the first few lines of the formatted chat data
                    for formatted_data in formatted_chats:
                        results.append((db_path, "\n".join(formatted_data.splitlines()[:10]) + "\n..."))

        # Print all results at the end
        console.print('\n\n')
        if results:
            for db_path, result in results:
                console.print(Markdown("---"))
                console.print(f"DATABASE: {os.path.join(os.path.basename(os.path.dirname(db_path)), os.path.basename(db_path))}\n")
                console.print(Markdown(result))
                console.print('\n\n')
        else:
            console.print("No results found.")

    except FileNotFoundError as e:
        error_message = f"File not found: {e}"
        logger.error(error_message)
        raise typer.Exit(code=1)
    except json.JSONDecodeError as e:
        error_message = f"JSON decode error: {e}"
        logger.error(error_message)
        raise typer.Exit(code=1)
    except Exception as e:
        error_message = f"Failed to discover and print chat data: {e}"
        logger.error(error_message)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()