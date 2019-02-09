import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    slug = Column(String(250), nullable=False)


class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    name = Column(String(80), nullable=False)
    slug = Column(String(250))
    description = Column(String(250))
    user_email = Column(String(250))
    category = relationship(
        Category,
        cascade="all, delete-orphan",
        single_parent=True,
    )


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
