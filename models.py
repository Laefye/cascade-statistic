from sqlalchemy import create_engine, Column, BigInteger, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
from os import getenv

# Настройка подключения к PostgreSQL
DATABASE_URL = getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Модель для сообщений
class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)

# Модель для голосовых сессий
class VoiceSession(Base):
    __tablename__ = 'voice_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp_in = Column(Integer)
    timestamp_out = Column(Integer)
    user_id = Column(Integer, index=True)
    guild_id = Column(Integer, index=True)

# Создание таблиц
def create_tables():
    Base.metadata.create_all(engine)

# Функции для добавления записей
def add_message(guild_id: int, user_id: int):
    session = Session()
    try:
        message = Message(guild_id=guild_id, user_id=user_id)
        session.add(message)
        session.commit()
    finally:
        session.close()

def add_voice_session(guild_id: int, user_id: int, timestamp_in: int, timestamp_out: int):
    session = Session()
    try:
        voice_session = VoiceSession(
            guild_id=guild_id,
            user_id=user_id,
            timestamp_in=timestamp_in,
            timestamp_out=timestamp_out
        )
        session.add(voice_session)
        session.commit()
    finally:
        session.close()

# Функции для получения статистики
def get_message_count(user_id: int, guild_id: int) -> int:
    session = Session()
    try:
        count = session.query(Message).filter(
            Message.user_id == user_id,
            Message.guild_id == guild_id
        ).count()
        return count
    finally:
        session.close()

def get_voice_session_duration(user_id: int, guild_id: int) -> int:
    session = Session()
    try:
        # Суммируем разницу timestamp_out - timestamp_in, игнорируя записи, где timestamp_out is NULL
        result = session.query(
            func.sum(VoiceSession.timestamp_out - VoiceSession.timestamp_in)
        ).filter(
            VoiceSession.user_id == user_id,
            VoiceSession.guild_id == guild_id,
            VoiceSession.timestamp_out.isnot(None)
        ).scalar()
        return result or 0  # Возвращаем 0, если результат None
    finally:
        session.close()

def get_top_by_messages(guild_id: int, top_n: int = 10):
    session = Session()
    try:
        results = session.query(
            Message.user_id,
            func.count(Message.id).label('message_count')
        ).filter(
            Message.guild_id == guild_id
        ).group_by(
            Message.user_id
        ).order_by(
            func.count(Message.id).desc()
        ).limit(top_n).all()
        return [(user_id, message_count) for user_id, message_count in results]
    finally:
        session.close()

def get_top_by_voice(guild_id: int, top_n: int = 10):
    session = Session()
    try:
        results = session.query(
            VoiceSession.user_id,
            func.sum(VoiceSession.timestamp_out - VoiceSession.timestamp_in).label('voice_duration')
        ).filter(
            VoiceSession.guild_id == guild_id,
            VoiceSession.timestamp_out.isnot(None)
        ).group_by(
            VoiceSession.user_id
        ).order_by(
            func.sum(VoiceSession.timestamp_out - VoiceSession.timestamp_in).desc()
        ).limit(top_n).all()
        return [(user_id, voice_duration) for user_id, voice_duration in results]
    finally:
        session.close()

create_tables()