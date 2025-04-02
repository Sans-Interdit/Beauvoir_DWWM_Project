from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "postgresql://postgres:test@127.0.0.1:5432/postgres"

Base = declarative_base()

class Account(Base):
    __tablename__ = 'account'
    
    id_account = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    age = Column(Integer)
    country = Column(String(50))
    gender = Column(String(10))

    conversations = relationship("Conversation", back_populates="account", cascade="all, delete-orphan")
    genres = relationship("Genre", secondary="account_genre", back_populates="accounts")

class AccountGenre(Base):
    __tablename__ = 'account_genre'
    
    id_account = Column(Integer, ForeignKey('account.id_account'), primary_key=True)
    id_genre = Column(Integer, ForeignKey('genre.id_genre'), primary_key=True)

class Genre(Base):
    __tablename__ = 'genre'
    
    id_genre = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    accounts = relationship("Account", secondary="account_genre", back_populates="genres")

    
class Conversation(Base):
    __tablename__ = 'conversation'
    
    id_conversation = Column(Integer, primary_key=True)
    id_account = Column(Integer, ForeignKey('account.id_account'))
    name = Column(String(100), nullable=False)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    account = relationship("Account", back_populates="conversations")
    recommendation = relationship("Recommendation", back_populates="conversation", cascade="all, delete-orphan", uselist=False)

    def to_dict(self):
        data = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        data["messages"] = [message.to_dict() for message in self.messages]
        data["recommendation"] = self.recommendation.to_dict() if self.recommendation else None
        return data

class Recommendation(Base):
    __tablename__ = 'recommendation'
    
    id_recommendation = Column(Integer, primary_key=True)
    id_conversation = Column(Integer, ForeignKey('conversation.id_conversation'), unique=True)
    oeuvres = Column(JSON)

    conversation = relationship("Conversation", back_populates="recommendation")

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class Message(Base):
    __tablename__ = 'message'
    
    id_message = Column(Integer, primary_key=True)
    id_conversation = Column(Integer, ForeignKey('conversation.id_conversation'))
    content = Column(String(2000), nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()





# tab = ["Supernatural", "Suspense", "Slice of Life", 'Gourmet', 'Avant Garde', 'Action', 'Science Fiction', 'Adventure', 
#        'Drama', 'Crime', 'Thriller', 'Fantasy', 'Comedy', 'Romance', 'Western', 'Mystery', 'War', 'Animation', 
#        'Family', 'Horror', 'Music', 'History', 'TV Movie', 'Documentary']

# # Créer les objets Genre à partir de la liste et les ajouter à la session
# genres_to_add = [Genre(name=genre) for genre in tab]

# # Ajouter les genres à la session
# session.add_all(genres_to_add)

# # Valider l'ajout dans la base de données
# session.commit()