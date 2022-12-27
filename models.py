from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, INT, ForeignKey, BOOLEAN, VARCHAR, TIMESTAMP

Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'

    id = Column(INT, primary_key=True)
    name = Column(VARCHAR(255), nulleble=True, unique=True)
    price = Column(INT, nulleble=True)


class Game(Base):
    __tablename__ = 'games'
    id = Column(INT, primary_key=True)
    categpry_id = Column(INT, ForeignKey('categories.id', ondelete='CASCADE'))
    name = Column(VARCHAR(255), nulleble=True, unique=True)
    description = Column(VARCHAR(255))
    price = Column(INT, ForeignKey('categories.price', ondelete='CASCADE'))
    player_max_count = Column(INT, nulleble=True)
    is_role_play = Column(BOOLEAN)


class GameRole(Base):
    __tablename__ = 'game_roles'

    id = Column(INT, primary_key=True)
    name = Column(VARCHAR(255), nulleble=True)
    short_description = Column(VARCHAR(255))
    man_gender = Column(BOOLEAN, nulleble=True)
    description = Column(VARCHAR(255), nulleble=True)
    game_id = Column(INT, ForeignKey('games.id', ondelete='CASCADE'))


class Event(Base):
    __tablename__ = 'events'

    id = Column(INT, primary_key=True)
    game_id = Column(INT, ForeignKey('games.id', ondelete='CASCADE'))
    data_start = Column(TIMESTAMP)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(INT, primary_key=True)
    name = Column(VARCHAR(255), nulleble=True, unique=True)


class User(Base):
    __tablename__ = 'users'

    id = Column(INT, primary_key=True)
    role_id = Column(INT, ForeignKey('roles.id', ondelete='CASCADE'))
    man_gender = Column(BOOLEAN, nulleble=True)


class EventPlayer(Base):
    __tablename__ = 'events_players'

    id = Column(INT, primary_key=True)
    user_id = Column(INT, ForeignKey('users.id', ondelete='CASCADE'))
    event_id = Column(INT, ForeignKey('events.id', ondelete='CASCADE'))
    game_role_id = Column(INT, ForeignKey('game+roles.id', ondelete='CASCADE'))
    is_reserved = Column(BOOLEAN)
