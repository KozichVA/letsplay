from sqlalchemy import Column, SMALLINT, BIGINT, ForeignKey, BOOLEAN, VARCHAR, TIMESTAMP, select, DECIMAL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    id = Column(SMALLINT, primary_key=True)

    engine = create_async_engine('postgresql+asyncpg://axlamon:axlamon@localhost:5432/letsplay')
    session = async_sessionmaker(bind=engine)

    @staticmethod
    def create_async_session(func):
        async def wrapper(*args, **kwargs):
            async with Base.session() as session:
                return await func(*args, **kwargs, session=session)

        return wrapper

    @create_async_session
    async def save(self, session: AsyncSession = None) -> None:
        session.add(self)
        await session.commit()
        await session.refresh(self)

    @create_async_session
    async def delete(self, session: AsyncSession = None) -> None:
        await session.delete(self)
        await session.commit()

    @classmethod
    @create_async_session
    async def get(cls, pk: int, session: AsyncSession = None):
        return await session.get(cls, pk)

    @classmethod
    @create_async_session
    async def all(cls, order_by='id', session: AsyncSession = None, **kwargs):
        return await session.scalars(select(cls).filter_by(**kwargs).order_by(order_by))


class Category(Base):
    __tablename__ = 'categories'

    name = Column(VARCHAR(255), nullable=False, unique=True)
    price = Column(DECIMAL(8, 2), nullable=True)


class Game(Base):
    __tablename__ = 'games'

    category_id = Column(SMALLINT, ForeignKey('categories.id', ondelete='CASCADE'))
    name = Column(VARCHAR(255), nullable=False, unique=True)
    picture = Column(VARCHAR(255))
    description = Column(VARCHAR(2048))
    rules = Column(VARCHAR(255))
    price = Column(DECIMAL(8, 2), nullable=True)
    player_max_count = Column(SMALLINT)
    difficulty_level = Column(SMALLINT)
    master_url = Column(VARCHAR(255), nullable=True)


class Tag(Base):
    __tablename__ = 'tags'

    name = Column(VARCHAR(255), nullable=False, unique=True)
    category_id = Column(SMALLINT, ForeignKey('categories.id', ondelete='CASCADE'))


class GameTag(Base):
    __tablename__ = 'game_tags'

    game_id = Column(SMALLINT, ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    tag_id = Column(SMALLINT, ForeignKey('tags.id', ondelete='CASCADE'), nullable=False)


class GameRole(Base):
    __tablename__ = 'game_roles'

    name = Column(VARCHAR(255), nullable=False)
    is_man = Column(BOOLEAN, nullable=True)
    description = Column(VARCHAR(255), nullable=False)
    url = Column(VARCHAR(255), nullable=True)
    game_id = Column(SMALLINT, ForeignKey('games.id', ondelete='CASCADE'), nullable=False)



class Event(Base):
    __tablename__ = 'events'

    game_id = Column(SMALLINT, ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    start_date = Column(TIMESTAMP, nullable=False)


class Role(Base):
    __tablename__ = 'roles'

    name = Column(VARCHAR(10), nullable=False, unique=True)


class User(Base):
    __tablename__ = 'users'

    id = Column(BIGINT, primary_key=True)
    role_id = Column(SMALLINT, ForeignKey('roles.id', ondelete='RESTRICT'), nullable=False)
    is_man = Column(BOOLEAN, nullable=True)


class EventPlayer(Base):
    __tablename__ = 'events_players'

    user_id = Column(SMALLINT, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(SMALLINT, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    game_role_id = Column(SMALLINT, ForeignKey('game_roles.id', ondelete='CASCADE'), nullable=False)
    is_reserved = Column(BOOLEAN, default=False)
