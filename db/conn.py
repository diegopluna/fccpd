import psycopg2

class DatabaseConnection:
    def __init__(self):
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            database="fccpd",
            user="postgres",
            password="admin",
            host="localhost",
            port="5435"
        )
    
    def get_connection(self):
        return self.connection_pool.getconn()

    def return_connection(self, connection):
        self.connection_pool.putconn(connection)

    def close_all_connections(self):
        self.connection_pool.closeall()