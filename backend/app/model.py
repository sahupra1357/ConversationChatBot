import uuid

from sqlmodel import SQLModel, Field, Relationship, Column
from datetime import datetime

class InsertUser(SQLModel):
    username: str = Field(unique=True, nullable=False)
    password: str  # Required, not nullable
    email: str | None = Field(default=None)
    name: str | None = Field(default=None)
    avatar: str | None = Field(default=None)

class Users(InsertUser, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversations: list["Conversations"] = Relationship(back_populates="users")

class InsertConversation(SQLModel):
    user_id: str = Field(foreign_key="users.id")
    title: str | None = Field(default=None)

class Conversations(InsertConversation, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    users: Users = Relationship(back_populates="conversations")
    messages: list["Messages"] = Relationship(back_populates="conversation")

class InsertMessage(SQLModel):
    conversation_id: str = Field(foreign_key="conversations.id")
    content: str # Required
    is_bot: bool = Field(default=False)

class Messages(InsertMessage, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    conversation: Conversations = Relationship(back_populates="messages")


