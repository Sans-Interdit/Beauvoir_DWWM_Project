from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
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
    
    # Relationships
    conversations = relationship("Conversation", secondary="message", back_populates="accounts")
    sent_messages = relationship("Message", foreign_keys="Message.from_user", back_populates="sender")
    received_messages = relationship("Message", back_populates="receiver")

class Conversation(Base):
    __tablename__ = 'conversation'
    
    id_conversation = Column(Integer, primary_key=True)
    name = Column(String)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation")
    accounts = relationship("Account", secondary="message", back_populates="conversations")

class Message(Base):
    __tablename__ = 'message'
    
    id_message = Column(Integer, primary_key=True)
    from_user = Column(Integer, ForeignKey('account.id_account'))
    to_account = Column(Integer, ForeignKey('account.id_account'))
    conversation_id = Column(Integer, ForeignKey('conversation.id_conversation'))
    content = Column(String)
    
    # Relationships
    sender = relationship("Account", foreign_keys=[from_user], back_populates="sent_messages")
    receiver = relationship("Account", foreign_keys=[to_account], back_populates="received_messages")
    conversation = relationship("Conversation", back_populates="messages")

# Create engine instance
engine = create_engine(DATABASE_URL)

# Create tables in the database
Base.metadata.create_all(engine)

# Check if tables exist
from sqlalchemy import inspect
inspector = inspect(engine)

# for table in ['account', 'conversation', 'message']:
#     if table in inspector.get_table_names():
#         print(f"Table '{table}' exists.")
#     else:
#         print(f"Table '{table}' doesn't exist.")