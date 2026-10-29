import sqlite3
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine


db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def enable_foreign_keys(connection, _):
    if isinstance(connection, sqlite3.Connection):
        connection.execute("PRAGMA foreign_keys=ON")


def init_database(app):
    schema = Path(app.root_path, "schema.sql").read_text(encoding="utf-8")
    with app.app_context():
        import models  # Register the ORM models before creating the tables.

        connection = db.engine.raw_connection()
        try:
            connection.executescript(schema)
            connection.commit()
        finally:
            connection.close()
        db.create_all()
        seed_catalog()


def seed_catalog():
    from models import InventoryLevel, PaymentMethod, Product, ProductCategory

    if not db.session.query(ProductCategory).first():
        category = ProductCategory(name="Essentials")
        db.session.add(category)
        db.session.flush()
        for name, price, sku in (("Water Bottle", 50, "DRINK-001"), ("Parking Cover", 100, "AUTO-001"), ("Air Freshener", 150, "AUTO-002")):
            product = Product(name=name, price=price, sku=sku, category_id=category.id, is_active=True)
            db.session.add(product)
            db.session.flush()
            db.session.add(InventoryLevel(product_id=product.id, quantity_on_hand=100))
    if not db.session.query(PaymentMethod).first():
        db.session.add_all([PaymentMethod(name="Cash"), PaymentMethod(name="Card")])
    db.session.commit()
