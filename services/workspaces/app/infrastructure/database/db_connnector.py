import os

import psycopg
from psycopg.rows import dict_row

class DbConnector:
    def connect(self):
        return psycopg.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            row_factory=dict_row,
        )