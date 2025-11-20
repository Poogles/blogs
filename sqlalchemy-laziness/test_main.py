import pytest
from sqlalchemy import create_engine, Engine, Integer, String, ForeignKey, select, event
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    relationship,
    sessionmaker,
    scoped_session,
    selectinload,
)

import main
import factories


logs = []


@pytest.fixture(scope="function")
def test_session():
    engine = create_engine("sqlite://", echo=False)

    main.Base.metadata.create_all(engine)

    Session = scoped_session(sessionmaker(bind=engine))
    factories.session_factory = lambda: Session()

    session = Session()
    # Patch the factories.
    factories.OrderFactory._meta.sqlalchemy_session = session
    factories.ItemFactory._meta.sqlalchemy_session = session

    # Generate test data using factory_boy
    # 3 orders, each with 2 items
    for _ in range(3):
        order = factories.OrderFactory()
        items = factories.ItemFactory.create_batch(2, order=order)

    session.commit()

    return session


def query_n_plus_one_occurs(test_session):
    """SQL generated is...

    'SELECT orders.id, orders.customer
        FROM orders'
    'SELECT items.id AS items_id, items.order_id AS items_order_id, items.product AS items_product
        FROM items
        WHERE :param_1 = items.order_id'
    'SELECT items.id AS items_id, items.order_id AS items_order_id, items.product AS items_product
        FROM items
        WHERE :param_1 = items.order_id'
    'SELECT items.id AS items_id, items.order_id AS items_order_id, items.product AS items_product
        FROM items
        WHERE :param_1 = items.order_id'

    """
    statement = select(main.Order)
    orders = test_session.execute(statement).scalars().all()

    items = []
    for order in orders:
        for item in order.items:
            items.append(item.id)
            item.product

    logs.append("query_n_plus_one_occurs complete")
    return items


def query_simple_join(test_session):
    """SQL generated is...

    'SELECT orders.id, orders.customer
        FROM orders JOIN items ON orders.id = items.order_id'
    'SELECT items.id AS items_id, items.order_id AS items_order_id, items.product AS items_product
        FROM items
        WHERE :param_1 = items.order_id'
    'SELECT items.id AS items_id, items.order_id AS items_order_id, items.product AS items_product
        FROM items
        WHERE :param_1 = items.order_id'


    """
    statement = select(main.Order).join(main.Item)
    # This unique is required.
    orders = test_session.execute(statement).unique().scalars().all()

    items = []
    for order in orders:
        for item in order.items:
            items.append(item.id)

    logs.append("query_simple_join complete")

    return items


def query_selectinload_prevents_n_plus_one(test_session):
    """SQL generated is...

    'SELECT orders.id, orders.customer
        FROM orders JOIN items ON orders.id = items.order_id'
    'SELECT items.order_id AS items_order_id, items.id AS items_id, items.product AS items_product
        FROM items
        WHERE items.order_id IN (__[POSTCOMPILE_primary_keys])'
    """
    stmt = select(main.Order).join(main.Item).options(selectinload(main.Order.items))
    orders = test_session.execute(stmt).unique().scalars().all()

    items = []
    for order in orders:
        for item in order.items:
            items.append(item.id)
            item.product

    logs.append("query_selectinload_prevents_n_plus_one complete")
    return items


def test_all_methods_identical(test_session):
    @event.listens_for(Engine, "before_execute")
    def only_real_exec(conn, clauseelement, multiparams, params, execution_options):
        global logs
        logs.append(str(clauseelement))

    # This is lazyloading
    orders1 = query_n_plus_one_occurs(test_session)
    # This is joined loading
    orders2 = query_simple_join(test_session)
    # This uses selectinload
    orders3 = query_selectinload_prevents_n_plus_one(test_session)

    # Each order has 6 items in total.
    assert orders1 == orders2 == orqders3 == [1, 2, 3, 4, 5, 6]
    assert logs == [
        "SELECT orders.id, orders.customer \nFROM orders",
        "SELECT items.id AS items_id, items.order_id AS items_order_id, items.product AS items_product \nFROM items \nWHERE :param_1 = items.order_id",
        "SELECT items.id AS items_id, items.order_id AS items_order_id, items.product AS items_product \nFROM items \nWHERE :param_1 = items.order_id",
        "SELECT items.id AS items_id, items.order_id AS items_order_id, items.product AS items_product \nFROM items \nWHERE :param_1 = items.order_id",
        "query_n_plus_one_occurs complete",
        "SELECT orders.id, orders.customer \nFROM orders JOIN items ON orders.id = items.order_id",
        "SELECT items.id AS items_id, items.order_id AS items_order_id, items.product AS items_product \nFROM items \nWHERE :param_1 = items.order_id",
        "SELECT items.id AS items_id, items.order_id AS items_order_id, items.product AS items_product \nFROM items \nWHERE :param_1 = items.order_id",
        "query_simple_join complete",
        "SELECT orders.id, orders.customer \nFROM orders JOIN items ON orders.id = items.order_id",
        "SELECT items.order_id AS items_order_id, items.id AS items_id, items.product AS items_product \nFROM items \nWHERE items.order_id IN (__[POSTCOMPILE_primary_keys])",
        "query_selectinload_prevents_n_plus_one complete",
    ]
