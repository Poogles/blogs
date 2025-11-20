import factory
from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy.orm import Session

import main


class OrderFactory(SQLAlchemyModelFactory):
    class Meta:
        model = main.Order
        sqlalchemy_session = None  # this gets patched
        sqlalchemy_session_persistence = "flush"

    customer = factory.Faker("name")


class ItemFactory(SQLAlchemyModelFactory):
    class Meta:
        model = main.Item
        sqlalchemy_session = None  # this gets patched
        sqlalchemy_session_persistence = "flush"

    product = factory.Faker("word")
    order = factory.SubFactory(OrderFactory)
