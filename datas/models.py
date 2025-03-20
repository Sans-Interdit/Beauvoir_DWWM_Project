from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "postgresql://postgres:test@127.0.0.1:5432/postgres"

Base = declarative_base()

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
    id_account = Column(Integer, ForeignKey('account.id_account'))
    name = Column(String)
    recommendations = Column(JSON)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    account = relationship("Account", back_populates="conversations")

    def to_dict(self):
        data = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        data["messages"] = [message.to_dict() for message in self.messages]
        return data


class Message(Base):
    __tablename__ = 'message'
    
    id_message = Column(Integer, primary_key=True)
    id_conversation = Column(Integer, ForeignKey('conversation.id_conversation'))
    content = Column(String)

    conversation = relationship("Conversation", back_populates="messages")

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()