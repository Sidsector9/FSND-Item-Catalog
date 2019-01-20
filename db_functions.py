from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup_catalog import Base, Category, Items
from flask import session as login_session
import random
import string

engine = create_engine(
    'sqlite:///catalog.db',
    connect_args={
        'check_same_thread': False})

DBSession = sessionmaker(bind=engine, autoflush=True)
session = DBSession()


def get_latest_items():
    """Returns the latest items added to the items table."""
    latest_items = session.query(
        Items.name,
        Items.slug,
        Category.name,
        Category.slug).filter_by(
        category_id=Category.id).order_by(
            desc(
                Items.id)).limit(10)
    return latest_items


def get_categories():
    """Returns all the categories."""
    return session.query(Category)


def get_category_name_by_category_slug(category_slug):
    """Returns category name by it's slug"""
    return session.query(Category.name).filter_by(slug=category_slug)


def get_items_by_category_slug(category_slug):
    """Returns all the items in a category by category slug."""
    category_id = session.query(
        Category.id).filter_by(
        slug=category_slug).first()[0]
    return session.query(Items).filter(category_id == Items.category_id)


def get_items_by_category_id(category_id):
    """Returns all the items in a category by category id."""
    return session.query(Items).filter(category_id == Items.category_id)


def get_item_description(item_slug):
    """Get item description by item slug."""
    return session.query(
        Items.description).filter_by(
        slug=item_slug).first()[0]


def get_item_by_slug(item_slug):
    """Get an item by item slug."""
    return session.query(Items).filter_by(slug=item_slug).first()


def get_state():
    """Generate a 32 character string as a session state and return it."""
    state = ''.join(
        random.choice(
            string.ascii_uppercase +
            string.digits) for x in xrange(32))
    login_session['state'] = state
    return login_session['state']
