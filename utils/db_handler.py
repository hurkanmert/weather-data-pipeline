import mysql.connector
from utils.logger import get_logger

logger = get_logger("db_handler")


class DBHandler:
    def __init__(self, host: str, user: str, password: str,
                 database: str, port: int = 3306):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port
        }
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor()
            logger.info(f"Database connection established: {self.config['database']}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def execute(self, query: str, data: tuple):
        try:
            self.cursor.execute(query, data)
            self.connection.commit()
            logger.info("Query executed successfully.")
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Database connection closed.")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()