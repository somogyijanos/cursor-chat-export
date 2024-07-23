import os
import sqlite3
import yaml
from typing import Any
from loguru import logger

class VSCDBQuery:
    def __init__(self, db_path: str) -> None:
        """
        Initialize the VSCDBQuery with the path to the SQLite database.

        Args:
            db_path (str): The path to the SQLite database file.
        """
        self.db_path = db_path
        logger.info(f"Database path: {os.path.join(os.path.basename(os.path.dirname(self.db_path)), os.path.basename(self.db_path))}")

    def query_to_json(self, query: str) -> list[Any] | dict[str, str]:
        """
        Execute a SQL query and return the results as a JSON-compatible list.

        Args:
            query (str): The SQL query to execute.

        Returns:
            list[Any] | dict[str, str]: The query results as a list, or an error message as a dictionary.
        """
        try:
            logger.debug(f"Executing query: {query}")
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
            with open('config.yml', 'r') as config_file:
                config = yaml.safe_load(config_file)
            query = config['aichat_query']
            logger.debug("Loaded AI chat query from config.yaml")
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


