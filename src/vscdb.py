import os
import sqlite3
import yaml
import json
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
        """Query the AI chat data from the database."""
        try:
            with open('config.yml', 'r') as config_file:
                config = yaml.safe_load(config_file)
            query = config['aichat_query']
            logger.debug("Loaded AI chat query from config.yaml")
            results = self.query_to_json(query)

            # Log the structure of each result
            for i, result in enumerate(results):
                try:
                    data = json.loads(result)
                    logger.debug(f"Data structure {i}:")
                    if isinstance(data, dict):
                        logger.debug(f"Keys: {list(data.keys())}")
                        # Log a sample of the data structure
                        logger.debug(f"Sample: {json.dumps(data, indent=2)[:500]}...")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse result {i}: {e}")

            return results
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": str(e)}

    def list_tables(self) -> list[str]:
        """List all tables in the database.
        
        Returns:
            list[str]: List of table names
        """
        try:
            conn = sqlite3.connect(f'file:{self.db_path}?mode=ro', uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            logger.info("Available tables:")
            for table in tables:
                logger.info(f"  - {table[0]}")
            return [table[0] for table in tables]
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return []

    def inspect_table(self, table_name: str, limit: int = 5) -> None:
        """Inspect the contents of a table.
        
        Args:
            table_name (str): Name of the table to inspect
            limit (int): Number of rows to show
        """
        try:
            conn = sqlite3.connect(f'file:{self.db_path}?mode=ro', uri=True)
            cursor = conn.cursor()

            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            logger.info(f"\nColumns in {table_name}:")
            for col in columns:
                logger.info(f"  - {col[1]} ({col[2]})")

            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            rows = cursor.fetchall()
            logger.info(f"\nSample data from {table_name} (first {limit} rows):")
            for row in rows:
                logger.info(f"  {row}")

            # For ItemTable, which likely has key-value pairs, let's also look for chat-related keys
            if table_name == 'ItemTable':
                cursor.execute("""
                    SELECT [key], substr(value, 1, 100) as preview 
                    FROM ItemTable 
                    WHERE [key] LIKE '%chat%' OR [key] LIKE '%composer%'
                """)
                chat_rows = cursor.fetchall()
                if chat_rows:
                    logger.info("\nChat-related entries found:")
                    for key, preview in chat_rows:
                        logger.info(f"  Key: {key}")
                        logger.info(f"  Preview: {preview}...")
                        logger.info("  ---")

            conn.close()
        except Exception as e:
            logger.error(f"Error inspecting table {table_name}: {e}")

# Example usage:
# db_query = VSCDBQuery('/Users/somogyijanos/Library/Application Support/Cursor/User/workspaceStorage/b989572f2e2186b48b808da2da437416/state.vscdb')
# json_result = db_query.query_to_json("SELECT value FROM ItemTable WHERE [key] IN ('workbench.panel.aichat.view.aichat.chatdata');")
# print(json_result)
