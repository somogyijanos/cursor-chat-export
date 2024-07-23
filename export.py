#!/usr/bin/env python

import os
import typer
from src.vscdb import VSCDBQuery
from src.export import ChatExporter, MarkdownChatFormatter, MarkdownFileSaver
import json

app = typer.Typer()

@app.command()
def export_chat(db_path: str, output_file: str, image_dir: str = None):
    """
    Export chat data from the database to a markdown file.

    Args:
        db_path (str): The path to the SQLite database file.
        output_file (str): The path to the output markdown file.
        image_dir (str): The directory where images will be saved. Defaults to 'images' next to output_file.
    """
    if image_dir is None:
        image_dir = os.path.join(os.path.dirname(output_file), 'images')

    try:
        # Query the AI chat data from the database
        db_query = VSCDBQuery(db_path)
        chat_data = db_query.query_aichat_data()

        if "error" in chat_data:
            typer.echo(f"Error querying chat data: {chat_data['error']}")
            raise typer.Exit(code=1)

        # Convert the chat data from JSON string to dictionary
        chat_data_dict = json.loads(chat_data[0])

        # Format and save the chat data
        formatter = MarkdownChatFormatter()
        saver = MarkdownFileSaver()
        exporter = ChatExporter(formatter, saver)
        exporter.export(chat_data_dict, output_file, image_dir)

        typer.echo(f"Chat data has been successfully exported to {output_file}")
    except Exception as e:
        typer.echo(f"Failed to export chat data: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

