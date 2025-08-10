from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from app.deps import SessionDep
from app.crud import create_message, get_messages_by_conversation_id
from app.model import InsertMessage, Messages

router = APIRouter(tags=["messages"])


@router.post("/messages", response_model=Messages)
def create_new_message(
    message: InsertMessage,
    session: SessionDep
):
    """
    Create a new message in a conversation.
    """
    if not message.conversation_id or not message.content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conversation ID and content are required.")
    
    new_message = create_message(session=session, message=message)
    return new_message


@router.get("/messages/{conversationId}", response_model=list[Messages])
def get_messages_by_conversation_id_route(
    conversationId: str,
    session: SessionDep
):
    """
    Get all messages for a specific conversation.
    """
    messages = get_messages_by_conversation_id(session=session, conversation_id=conversationId)
    if not messages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No messages found for this conversation.")
    return messages

