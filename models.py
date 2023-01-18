from sqlalchemy.orm import declarative_base, declarative_mixin, sessionmaker
from sqlalchemy import Column, INT, ForeignKey, BOOLEAN, VARCHAR, TIMESTAMP, create_engine, select

Base = declarative_base()
@declarative_mixin
class Basemixin(object):
    id = Column(INT, primary_key=True)

    engine = create_engine('postgresql://axlamon:axlamon@localhost:5432/letsplay')
    session = sessionmaker(bind=engine)
    @staticmethod
    def create_async_session(func):
        async def wrapper(*args, **kwargs):
            async with Base.session() as session:
                return await func(*args, **kwargs, session=session)

    @create_async_session
    async def save(self, session) -> None:
        await session.add(self)
        await session.commit()
        await session.refresh(self)
    @create_async_session
    async def delete(self, session) -> None:
        await session.delete(self)
        await session.commit()

    @create_async_session
    @classmethod
    async def get(cls, pk: int, session):
        return await session.get(cls, pk)

    @create_async_session
    @classmethod
    async def all(cls, order_by,  session, **kwargs):
        return await session.scalars(select(cls).filter_by(kwargs).order_by(order_by))


class Category(Base, Basemixin):
    __tablename__ = 'categories'
    id = Column(INT, primary_key=True)
    name = Column(VARCHAR(255), nullable=True, unique=True)
    price = Column(INT, nullable=True)

class Game(Base):
    __tablename__ = 'games'
    id = Column(INT, primary_key=True)
    categpry_id = Column(INT, ForeignKey('categories.id', ondelete='CASCADE'))
    name = Column(VARCHAR(255), nullable=True, unique=True)
    description = Column(VARCHAR(255))
    price = Column(INT, nullable=True)
    player_max_count = Column(INT, nullable=True)
    is_role_play = Column(BOOLEAN)


class GameRole(Base):
    __tablename__ = 'game_roles'

    id = Column(INT, primary_key=True)
    name = Column(VARCHAR(255), nullable=True)
    short_description = Column(VARCHAR(255))
    man_gender = Column(BOOLEAN, nullable=True)
    description = Column(VARCHAR(255), nullable=True)
    game_id = Column(INT, ForeignKey('games.id', ondelete='CASCADE'))


class Event(Base):
    __tablename__ = 'events'

    id = Column(INT, primary_key=True)
    game_id = Column(INT, ForeignKey('games.id', ondelete='CASCADE'))
    data_start = Column(TIMESTAMP)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(INT, primary_key=True)
    name = Column(VARCHAR(255), nullable=True, unique=True)


class User(Base):
    __tablename__ = 'users'

    id = Column(INT, primary_key=True)
    role_id = Column(INT, ForeignKey('roles.id', ondelete='CASCADE'))
    man_gender = Column(BOOLEAN, nullable=True)


class EventPlayer(Base):
    __tablename__ = 'events_players'

    id = Column(INT, primary_key=True)
    user_id = Column(INT, ForeignKey('users.id', ondelete='CASCADE'))
    event_id = Column(INT, ForeignKey('events.id', ondelete='CASCADE'))
    game_role_id = Column(INT, ForeignKey('game_roles.id', ondelete='CASCADE'))
    is_reserved = Column(BOOLEAN)
