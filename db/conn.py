from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager


from .schema import Base

class DatabaseConnection:
    def __init__(self):
        # Database connection URL
        self.DATABASE_URL = "postgresql://postgres:admin@localhost:5432/postgres"
        
        self.engine = None
        self.Session = None

    def connect(self):
        try:
            self.engine = create_engine(self.DATABASE_URL, echo=True)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
            
            print("Successfully connected to the database!")
            return True
            
        except SQLAlchemyError as e:
            print(f"Error connecting to the database: {str(e)}")
            return False

    @contextmanager
    def get_session(self):
        if not self.Session:
            raise Exception("Database not connected. Call connect() first.")
        
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()