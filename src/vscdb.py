import os
import sqlite3
import yaml
from typing import Any
from loguru import logger

class VSCDBQuery:
    def __init__(self, db_path: str, config_path: str) -> None:
        """
        Initialize the VSCDBQuery with the path to the SQLite database and the config file.

        Args:
            db_path (str): The path to the SQLite database file.
            config_path (str): The path to the config.yml file.
        """
        self.db_path = db_path
        self.config_path = config_path
        logger.info(f"Database path: {os.path.join(os.path.basename(os.path.dirname(self.db_path)), os.path.basename(self.db_path))}")
        # logger.debug(f"Current working directory: {os.getcwd()}")
        # logger.debug(f"Expected config path: {self.config_path}")

    def query_to_json(self, query: str) -> list[Any] | dict[str, str]:
        """
        Execute a SQL query and return the results as a JSON-compatible list.

        Args:
            query (str): The SQL query to execute.

        Returns:
            list[Any] | dict[str, str]: The query results as a list, or an error message as a dictionary.
        """
        try:
            # logger.debug(f"Executing query: {query}")
            conn = sqlite3.connect(f'file:{self.db_path}?mode=ro', uri=True)
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()

            # Assuming the query returns rows with a single column
            result = [row[0] for row in rows]
            logger.success(f"Query executed successfully, fetched {len(result)} rows.")
            return result
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": str(e)}
        
    def query_aichat_data(self) -> list[Any] | dict[str, str]:
        """
        Query the AI chat data from the database.

        Returns:
            list[Any] | dict[str, str]: The AI chat data as a list, or an error message as a dictionary.
        """
        try:
            # logger.debug(f"Attempting to open config file at: {self.config_path}")
            with open(self.config_path, 'r') as config_file:
                config = yaml.safe_load(config_file)
            query = config['aichat_query']
            # logger.debug(f"Loaded AI chat query from {self.config_path}")
            return self.query_to_json(query)
        except FileNotFoundError as e:
            logger.error(f"Config file not found: {e}")
            return {"error": str(e)}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": str(e)}

# Example usage:
# db_query = VSCDBQuery('/Users/somogyijanos/Library/Application Support/Cursor/User/workspaceStorage/b989572f2e2186b48b808da2da437416/state.vscdb')
# json_result = db_query.query_to_json("SELECT value FROM ItemTable WHERE [key] IN ('workbench.panel.aichat.view.aichat.chatdata');")
# print(json_result)