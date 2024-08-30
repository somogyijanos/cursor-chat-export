import re
import shutil
import os
import json
from abc import ABC, abstractmethod
from typing import Any
from loguru import logger
import traceback

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
        try:
            formatted_chats = []
            for tab_index, tab in enumerate(chat_data['tabs']):
                bubbles = tab['bubbles']
                formatted_chat = [f"# Chat Transcript - Tab {tab_index + 1}\n"]
                tab_image_dir = os.path.join(image_dir, f"tab_{tab_index + 1}") if image_dir else None
                if tab_image_dir is not None:
                    os.makedirs(tab_image_dir, exist_ok=True)

                for bubble in bubbles:
                    if bubble['type'] == 'user':
                        user_text = ["## User:\n\n"]
                        
                        if "selections" in bubble and bubble["selections"]:
                            user_text.append(f"[selections]  \n{"\n".join([s["text"] for s in bubble['selections']])}")
                        
                        if 'image' in bubble and tab_image_dir is not None:
                            image_path = bubble['image']['path']
                            image_filename = os.path.basename(image_path)
                            new_image_path = os.path.join(tab_image_dir, image_filename)
                            shutil.copy(image_path, new_image_path)
                            user_text.append(f"[image]  \n![User Image]({new_image_path})")
                        
                        if "delegate" in bubble:
                            if bubble["delegate"]:
                                user_text_text = bubble['delegate']["a"]
                            else:
                                user_text_text = ""
                        elif "text" in bubble:
                            if bubble["text"]:
                                user_text_text = bubble['text']
                            else:
                                user_text_text = ""
                        elif "initText" in bubble:
                            if bubble["initText"]:
                                user_text_text = bubble['rawText']
                                user_text_text = json.loads(bubble["initText"])['root']['children'][0]['children'][0]['text']
                            else:
                                user_text_text = ""
                        elif "rawText" in bubble:
                            if bubble["rawText"]:
                                user_text_text = bubble['text']
                            else:
                                user_text_text = ""
                        else:
                            user_text_text = "[ERROR: no user text found]"
                            logger.error(f"Couldn't find user text entry in one of the bubbles.")
                            logger.debug(f"Bubble:\n{json.dumps(bubble, indent=4)}")
                        if user_text_text:
                            user_text.append(f"[text]  \n{user_text_text}")
                        
                        user_text.append("\n")

                        if len(user_text) > 2:
                            formatted_chat.append("\n".join(user_text))
                    elif bubble['type'] == 'ai':
                        model_type = bubble.get('modelType', 'Unknown')
                        raw_text = re.sub(r'```python:[^\n]+', '```python', bubble['rawText'])
                        formatted_chat.append(f"## AI ({model_type}):\n\n{raw_text}\n")

                formatted_chats.append("\n".join(formatted_chat))

            logger.success("Chats formatted.")
            return formatted_chats
        except KeyError as e:
            logger.error(f"KeyError: Missing key {e} in chat data. Ensure the data structure is correct. Full error: {e}")
            return [f"Error: Missing key {e}"]
        except FileNotFoundError as e:
            logger.error(f"FileNotFoundError: {e}. Ensure the image paths are correct. Full error: {e}")
            return [f"Error: {e}"]
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}. Ensure the JSON data is correctly formatted. Full error: {e}")
            return [f"Error: {e}"]
        except Exception as e:
            logger.error(f"Unexpected error: {e}. Full traceback: {traceback.format_exc()}")
            return [f"Error: {e}"]

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