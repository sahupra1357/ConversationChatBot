from sqlmodel import Session, create_engine, select

from .config import local_settings
from .crud import create_user, create_conversation
from .model import Users, Conversations, Messages, InsertUser, InsertConversation, InsertMessage

engine = create_engine(str(local_settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(Users).where(Users.username == local_settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = InsertUser(
            username=local_settings.FIRST_SUPERUSER,
            password=local_settings.FIRST_SUPERUSER_PASSWORD,
            email="john@example.com",
            name="John Doe",
            avatar= None,
        )
        user = create_user(session=session, user=user_in)

    conversation = session.exec(
        select(Conversations).where(Conversations.user_id == user.id)
    ).first()
    if not conversation:
        conversation_in = InsertConversation(
            user_id=user.id,
            title="Getting Started Guide"
        )
        convers = create_conversation(session=session, conversation=conversation_in)

