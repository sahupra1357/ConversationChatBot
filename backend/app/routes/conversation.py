from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from app.deps import SessionDep
from app.crud import get_converstion_by_user_id, get_conversation_by_id, create_conversation, delete_conversation
from app.model import InsertConversation, Conversations
from app.model import Users


router = APIRouter(tags=["conversation"])

@router.get("/conversations/user/{userId}", response_model=list[Conversations])
def get_conversations_by_user_id(
    userId: str,
    session: SessionDep
):
    """
    Get all conversations for a specific user.
    """
    conversations = get_converstion_by_user_id(session=session, user_id=userId)
    if not conversations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No conversations found for this user.")
    return conversations

@router.post("/conversations", response_model=Conversations)
def create_new_conversation(
    conversation: InsertConversation,
    session: SessionDep
):
    """
    Create a new conversation for a user.
    """
    if not conversation.user_id or not conversation.title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID and title are required.")
    
    # existing_conversation = get_conversation_by_id(session=session, conversation_id=conversation.user_id)
    # if existing_conversation:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conversation already exists for this user.")
    
    new_conversation = create_conversation(session=session, conversation=conversation)
    return new_conversation

@router.delete("/conversations/{conversationId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation_by_id(
    conversationId: str,
    session: SessionDep
):
    """
    Delete a conversation by its ID.
    """
    conversation = get_conversation_by_id(session=session, conversation_id=conversationId)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    
    delete_conversation(session=session, conversation_id=conversationId)
    return {"detail": "Conversation deleted successfully."}

@router.get("/conversations/{conversationId}", response_model=Conversations)
def get_conversation_by_id_route(
    conversationId: str,
    session: SessionDep
):
    """
    Get a specific conversation by its ID.
    """
    conversation = get_conversation_by_id(session=session, conversation_id=conversationId)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    return conversation