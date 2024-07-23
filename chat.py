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

logger.remove()
logger.add(sys.stderr, level="INFO")


app = typer.Typer()
console = Console()

@app.command()
def export(db_path: str, output_dir: str = None):
    """
    Export chat data from the database to markdown files or print it to the command line.

    Args:
        db_path (str): The path to the SQLite database file.
        output_dir (str): The directory where the output markdown files will be saved. If not provided, prints to command line.
    """
    image_dir = os.path.join(output_dir, 'images') if output_dir else None

    try:
        # Query the AI chat data from the database
        db_query = VSCDBQuery(db_path)
        chat_data = db_query.query_aichat_data()

        if "error" in chat_data:
            error_message = f"Error querying chat data: {chat_data['error']}"
            logger.error(error_message)
            raise typer.Exit(code=1)

        # Convert the chat data from JSON string to dictionary
        chat_data_dict = json.loads(chat_data[0])

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

@app.command()
def discover(directory: str, limit: int = None, search_text: str = None):
    """
    Discover all state.vscdb files in a directory and its subdirectories, and print a few lines of dialogue.

    Args:
        directory (str): The directory to search for state.vscdb files.
        limit (int): The maximum number of state.vscdb files to process, sorted by most recent edits. Defaults to 10 if search_text is not provided, else -1.
        search_text (str): The text to search for in the chat history. If provided, only chat entries containing this text will be printed.
    """
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
                            # results.append((db_path, "[...]" + "  \n[...]  \n".join(filtered_lines[:10]) + "[...]"))
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
