from sqlalchemy.orm import declarative_base, declarative_mixin, sessionmaker
from sqlalchemy import Column, INT, ForeignKey, BOOLEAN, VARCHAR, TIMESTAMP, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

Base = declarative_base()


@declarative_mixin
class Basemixin(object):
    id = Column(INT, primary_key=True)

    engine = create_async_engine('postgresql+asyncpg://axlamon:axlamon@localhost:5432/letsplay')
    session = sessionmaker(bind=engine, class_=AsyncSession)

    @staticmethod
    def create_async_session(func):
        async def wrapper(*args, **kwargs):
            async with Basemixin.session() as session:
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
    async def all(cls, order_by='ID',  session: AsyncSession = None, **kwargs):
        return await session.scalars(select(cls).filter_by(kwargs).order_by(order_by))


class Category(Base, Basemixin):
    __tablename__ = 'categories'
    id = Column(INT, primary_key=True)
    name = Column(VARCHAR(255), nullable=True, unique=True)
    price = Column(INT, nullable=True)


class Game(Base, Basemixin):
    __tablename__ = 'games'

    id = Column(INT, primary_key=True)
    categpry_id = Column(INT, ForeignKey('categories.id', ondelete='CASCADE'))
    name = Column(VARCHAR(255), nullable=True, unique=True)
    description = Column(VARCHAR(255))
    price = Column(INT, nullable=True)
    player_max_count = Column(INT, nullable=True)
    is_role_play = Column(BOOLEAN)


class GameRole(Base, Basemixin):
    __tablename__ = 'game_roles'

    id = Column(INT, primary_key=True)
    name = Column(VARCHAR(255), nullable=True)
    short_description = Column(VARCHAR(255))
    man_gender = Column(BOOLEAN, nullable=True)
    description = Column(VARCHAR(255), nullable=True)
    game_id = Column(INT, ForeignKey('games.id', ondelete='CASCADE'))
    master = Column(VARCHAR(255), nullable=True)


class Event(Base, Basemixin):
    __tablename__ = 'events'

    id = Column(INT, primary_key=True)
    game_id = Column(INT, ForeignKey('games.id', ondelete='CASCADE'))
    data_start = Column(TIMESTAMP)


class Role(Base, Basemixin):
    __tablename__ = 'roles'

    id = Column(INT, primary_key=True)
    name = Column(VARCHAR(255), nullable=True, unique=True)


class User(Base, Basemixin):
    __tablename__ = 'users'

    id = Column(INT, primary_key=True)
    role_id = Column(INT, ForeignKey('roles.id', ondelete='CASCADE'))
    man_gender = Column(BOOLEAN, nullable=True)


class EventPlayer(Base, Basemixin):
    __tablename__ = 'events_players'

    id = Column(INT, primary_key=True)
    user_id = Column(INT, ForeignKey('users.id', ondelete='CASCADE'))
    event_id = Column(INT, ForeignKey('events.id', ondelete='CASCADE'))
    game_role_id = Column(INT, ForeignKey('game_roles.id', ondelete='CASCADE'))
    is_reserved = Column(BOOLEAN)
