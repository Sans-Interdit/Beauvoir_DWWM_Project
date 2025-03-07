from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database connection
DATABASE_URL = "postgresql://postgres:test@127.0.0.1:5432/postgres"

# Create Base instance
Base = declarative_base()

# Define models according to the ERD
class Account(Base):
    __tablename__ = 'account'
    
    id_account = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)
    preference = Column(JSON)

    conversations = relationship("Conversation", back_populates="account", cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = 'conversation'
    
    id_conversation = Column(Integer, primary_key=True)
    name = Column(String)
    account_id = Column(Integer, ForeignKey('account.id_account'))

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    account = relationship("Account", back_populates="conversations")

class Message(Base):
    __tablename__ = 'message'
    
    id_message = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversation.id_conversation'))
    content = Column(String)

    conversation = relationship("Conversation", back_populates="messages")


# Create engine instance
engine = create_engine(DATABASE_URL)

# Create tables in the database
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()