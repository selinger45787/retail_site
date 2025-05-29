from app import app, db
from models import Order

with app.app_context():
    # Создаем таблицу orders
    Order.__table__.create(db.engine)
    print("Таблица orders успешно создана") 