from fastapi import APIRouter
from app.routes import chatmessage, conversation, messages, users


api_router = APIRouter()
api_router.include_router(chatmessage.router)
api_router.include_router(conversation.router)
api_router.include_router(messages.router)
api_router.include_router(users.router)