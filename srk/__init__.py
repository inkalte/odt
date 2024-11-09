from sqlalchemy import Column, Integer, String, create_engine, Float, ForeignKey, DateTime, UniqueConstraint, Boolean, \
    Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

engine = create_engine('sqlite:///srk.sqlite', echo=False)
Base = declarative_base()


class Summary(Base):
    __tablename__ = 'summary'
    id: int = Column(Integer, primary_key=True)
    start_time: datetime = Column(DateTime)
    end_time: datetime = Column(DateTime)
    activity: str = Column(String)
    number: int = Column(Integer)
    entity: str = Column(String)
    schedule_name: str = Column(String)
    bytes: int = Column(Integer)
    mediaw: int = Column(Integer)
    successful: str = Column(String)
    volume_name: str = Column(String)
    comm_wait: int = Column(Integer)

    def __repr__(self):
        return f'{self.start_time} {self.end_time} {self.activity} {self.entity} {self.schedule_name}'


class Event(Base):
    __tablename__ = 'events'
    id: int = Column(Integer, primary_key=True)
    tsm_host: str = Column(String)
    scheduled_start: datetime = Column(DateTime)
    actual_start: datetime = Column(DateTime)
    domain_name: str = Column(String)
    schedule_name: str = Column(String)
    type: str = Column(String)
    node_name: str = Column(String)
    status: str = Column(String)
    checked: bool = Column(Boolean, default=False)
    error: str = Column(Text)
    result: str = Column(Integer)
    reason: str = Column(String)
    completed: datetime = Column(DateTime)
    size: int = Column(Integer)
    __table_args__ = (UniqueConstraint('domain_name', 'schedule_name', 'node_name', 'actual_start', name='schedule'),)

    def __repr__(self):
        return f'{self.id} | {self.scheduled_start} | {self.completed} | {self.type} | {self.node_name} |' \
               f' Size  {self.size} GB | {self.status} | {self.checked}'


Base.metadata.create_all(engine)
