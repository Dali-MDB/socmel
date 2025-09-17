from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import dotenv
import os
dotenv.load_dotenv()


# DATABASE_URL = os.getenv('DATABASE_URL')
# engine = create_engine(DATABASE_URL)
engine = create_engine('sqlite:///socmel.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
