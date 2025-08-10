import uuid
from typing import Any

from sqlmodel import Session, select

from .model import InsertUser, InsertConversation, InsertMessage, Users, Conversations, Messages
from .security import get_password_hash, verify_password

def create_user(*, session: Session, user: InsertUser) -> Users:
    #db_obj = Users.model_validate(user, update={"hashed_password": get_password_hash(user.password)})
    db_obj = Users.model_validate(user)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_converstion_by_user_id(*, session: Session, user_id: str) -> list[Conversations]:
    statement = select(Conversations).where(Conversations.user_id == user_id)
    results = session.exec(statement).all()
    return results

def get_conversation_by_id(*, session: Session, conversation_id: str) -> Conversations | None:
    statement = select(Conversations).where(Conversations.id == conversation_id)
    result = session.exec(statement).first()
    return result

def create_conversation(*, session: Session, conversation: InsertConversation) -> Conversations:
    db_obj = Conversations.model_validate(conversation, update={"user_id": conversation.user_id})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_conversation(*, session: Session, conversation_id: str) -> None:
    statement = select(Conversations).where(Conversations.id == conversation_id)
    result = session.exec(statement).first()
    if result:
        session.delete(result)
        session.commit()    

def getUserById(*, session: Session, user_id: str) -> Users | None:
    statement = select(Users).where(Users.id == user_id)
    result = session.exec(statement).first()
    return result

def get_messages_by_conversation_id(*, session: Session, conversation_id: str) -> list[Messages]:
    statement = select(Messages).where(Messages.conversation_id == conversation_id)
    results = session.exec(statement).all()
    return results

def create_message(*, session: Session, message: InsertMessage) -> Messages:
    db_obj = Messages.model_validate(message, update={"conversation_id": message.conversation_id})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj   

