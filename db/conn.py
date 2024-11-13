from psycopg2 import pool
from os import environ

class DatabaseConnection:
    def __init__(self):
        self.connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            database=environ.get('POSTGRES_DB', 'postgres'),
            user=environ.get('POSTGRES_USER', 'admin'),
            password=environ.get('POSTGRES_PASSWORD', 'admin'),
            host=environ.get('POSTGRES_HOST', 'localhost'),
            port=environ.get('POSTGRES_PORT', '5432')
        )
    
    def get_connection(self):
        return self.connection_pool.getconn()

    def return_connection(self, connection):
        self.connection_pool.putconn(connection)

    def close_all_connections(self):
        self.connection_pool.closeall()