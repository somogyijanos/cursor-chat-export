import re
import shutil
import os
from abc import ABC, abstractmethod
from typing import Any
from loguru import logger

class ChatFormatter(ABC):
    @abstractmethod
    def format(self, chat_data: dict[str, Any], image_dir: str = 'images') -> str:
        """Format the chat data into Markdown format.

        Args:
            chat_data (dict[str, Any]): The chat data to format.
            image_dir (str): The directory where images will be saved. Defaults to 'images'.

        Returns:
            str: The formatted chat data in Markdown.
        """
        pass

class MarkdownChatFormatter(ChatFormatter):
    def format(self, chat_data: dict[str, Any], image_dir: str | None = 'images') -> str:
        """Format the chat data into Markdown format.

        Args:
            chat_data (dict[str, Any]): The chat data to format.
            image_dir (str): The directory where images will be saved. Defaults to 'images'.

        Returns:
            str: The formatted chat data in Markdown.
        """
        formatted_chats = []
        for tab_index, tab in enumerate(chat_data['tabs']):
            bubbles = tab['bubbles']
            formatted_chat = [f"# Chat Transcript - Tab {tab_index + 1}\n"]
            tab_image_dir = os.path.join(image_dir, f"tab_{tab_index + 1}") if image_dir else None
            if tab_image_dir is not None:
                os.makedirs(tab_image_dir, exist_ok=True)

            for bubble in bubbles:
                if bubble['type'] == 'user':
                    user_message = bubble.get('delegate', {}).get('a', 'User message unavailable due to missing data.')
                    formatted_chat.append(f"## User:\n\n{user_message}\n")
                    if 'image' in bubble and tab_image_dir is not None:
                        image_path = bubble['image']['path']
                        image_filename = os.path.basename(image_path)
                        new_image_path = os.path.join(tab_image_dir, image_filename)
                        shutil.copy(image_path, new_image_path)
                        formatted_chat.append(f"![User Image]({new_image_path})\n")
                elif bubble['type'] == 'ai':
                    model_type = bubble.get('modelType', 'Unknown')
                    raw_text = re.sub(r'```python:[^\n]+', '```python', bubble.get('rawText', 'AI response unavailable.'))
                    formatted_chat.append(f"## AI ({model_type}):\n\n{raw_text}\n")

            formatted_chats.append("\n".join(formatted_chat))

        return formatted_chats

class FileSaver(ABC):
    @abstractmethod
    def save(self, formatted_data: str, file_path: str) -> None:
        """Save the formatted data to a file.

        Args:
            formatted_data (str): The formatted data to save.
            file_path (str): The path to the file where the data will be saved.
        """
        pass

class MarkdownFileSaver(FileSaver):
    def save(self, formatted_data: str, file_path: str) -> None:
        """Save the formatted data to a Markdown file.

        Args:
            formatted_data (str): The formatted data to save.
            file_path (str): The path to the Markdown file where the data will be saved.
        """
        try:
            with open(file_path, 'w') as file:
                file.write(formatted_data)
            logger.info(f"Chat has been formatted and saved as {file_path}")
        except IOError as e:
            logger.error(f"IOError: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

class ChatExporter:
    def __init__(self, formatter: ChatFormatter, saver: FileSaver) -> None:
        """Initialize the ChatExporter with a formatter and a saver.

        Args:
            formatter (ChatFormatter): The formatter to format the chat data.
            saver (FileSaver): The saver to save the formatted data.
        """
        self.formatter = formatter
        self.saver = saver

    def export(self, chat_data: dict[str, Any], output_dir: str, image_dir: str) -> None:
        """Export the chat data by formatting and saving it.

        Args:
            chat_data (dict[str, Any]): The chat data to export.
            output_dir (str): The directory where the formatted data will be saved.
            image_dir (str): The directory where images will be saved.
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            formatted_chats = self.formatter.format(chat_data, image_dir)
            for tab_index, formatted_data in enumerate(formatted_chats):
                tab_file_path = os.path.join(output_dir, f"tab_{tab_index + 1}.md")
                self.saver.save(formatted_data, tab_file_path)
        except Exception as e:
            logger.error(f"Failed to export chat data: {e}")

# Example usage:
# Load the chat data from the JSON file
# with open('chat.json', 'r') as file:
#     chat_data = json.load(file)

# formatter = MarkdownChatFormatter()
# saver = MarkdownFileSaver()
# exporter = ChatExporter(formatter, saver)
# exporter.export(chat_data, 'output_folder', 'images')