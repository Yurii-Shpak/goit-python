from datetime import datetime

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Table


Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    address = Column(String(80), nullable=True)
    phone1 = Column(String(14), nullable=True)
    phone2 = Column(String(14), nullable=True)
    phone3 = Column(String(14), nullable=True)
    email = Column(String(50), nullable=True)
    birthday = Column(Date(), nullable=True)
