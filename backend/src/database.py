import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

SQL_Alchemy_DB = os.getenv("DATABASE_URL", "sqlite:///./lumi.db")

engine = create_engine(
    SQL_Alchemy_DB, connect_args={"check_same_thread" : False}
)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

Base = declarative_base()