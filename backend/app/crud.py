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

def getUserByUsername(*, session: Session, username: str) -> Users | None:
    """
    Get a user by username with improved logging and error handling
    """
    if not username:
        print("Warning: Empty username provided to getUserByUsername")
        return None
        
    try:
        print(f"Looking up user with username: {username}")
        statement = select(Users).where(Users.username == username)
        result = session.exec(statement).first()
        
        if result:
            print(f"Found user: {result.username} with ID: {result.id}")
        else:
            print(f"No user found with username: {username}")
            
        return result
    except Exception as e:
        print(f"Error in getUserByUsername: {str(e)}")
        # Re-raise the exception to be handled by the caller
        raise

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

def delete_message_by_conversation_id(*, session: Session, conversation_id: str) -> None:
    # Using direct delete statement for bulk deletion - more efficient
    from sqlalchemy import delete
    delete_stmt = delete(Messages).where(Messages.conversation_id == conversation_id)
    session.execute(delete_stmt)
    session.commit()
    
    