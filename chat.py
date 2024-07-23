#!/usr/bin/env python

import os
import typer
from src.vscdb import VSCDBQuery
from src.export import ChatExporter, MarkdownChatFormatter, MarkdownFileSaver
from rich.console import Console
from loguru import logger
import json

app = typer.Typer()
console = Console()

@app.command()
def export(db_path: str, output_file: str = None, image_dir: str = None):
    """
    Export chat data from the database to a markdown file or print it to the command line.

    Args:
        db_path (str): The path to the SQLite database file.
        output_file (str): The path to the output markdown file. If not provided, prints to command line.
        image_dir (str): The directory where images will be saved. Defaults to 'images' next to output_file.
    """
    if output_file and image_dir is None:
        image_dir = os.path.join(os.path.dirname(output_file), 'images')

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
        formatted_data = formatter.format(chat_data_dict, image_dir)

        if output_file:
            # Save the chat data
            saver = MarkdownFileSaver()
            exporter = ChatExporter(formatter, saver)
            exporter.export(chat_data_dict, output_file, image_dir)
            success_message = f"Chat data has been successfully exported to {output_file}"
            logger.info(success_message)
        else:
            # Print the chat data to the command line
            console.print(formatted_data)
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
def discover(directory: str):
    """
    Discover all state.vscdb files in a directory and its subdirectories, and print a few lines of dialogue.

    Args:
        directory (str): The directory to search for state.vscdb files.
    """
    try:
        for root, _, files in os.walk(directory):
            if 'state.vscdb' in files:
                db_path = os.path.join(root, 'state.vscdb')
                db_query = VSCDBQuery(db_path)
                chat_data = db_query.query_aichat_data()

                if "error" in chat_data:
                    error_message = f"Error querying chat data from {db_path}: {chat_data['error']}"
                    logger.error(error_message)
                    continue

                if not chat_data:
                    logger.warning(f"No chat data found in {db_path}")
                    continue

                chat_data_dict = json.loads(chat_data[0])
                formatter = MarkdownChatFormatter()
                formatted_data = formatter.format(chat_data_dict)

                # Print the first few lines of the formatted chat data
                console.print("\n".join(formatted_data.splitlines()[:10]))
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
