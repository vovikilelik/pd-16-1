import os
import json

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey

from utils.misc import json_reader, serialize, create_serialize_mapper, print_pre

DATABASE_PATH = 'database.db'

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(String)
    email = Column(String)
    role = Column(String)
    phone = Column(String)


class Offer(db.Model):
    __tablename__ = 'offers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    executor_id = Column(Integer, ForeignKey('users.id'))


class Order(db.Model):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    address = Column(String)
    price = Column(Integer)
    customer_id = Column(Integer, ForeignKey('users.id'))
    executor_id = Column(Integer, ForeignKey('users.id'))


# Проверяем, существует ли файл базы. Если нет - будем генерировать
has_exists = os.path.isfile(DATABASE_PATH)
db.create_all()


def get_value(data, field):
    if field in data:
        return data[field]


def add_user(row):
    user = User(
        id=get_value(row, 'id'),
        first_name=row['first_name'],
        last_name=row['last_name'],
        age=row['age'],
        email=row['email'],
        role=row['role'],
        phone=row['phone']
    )

    db.session.add(user)


def add_offer(row):
    offer = Offer(
        id=get_value(row, 'id'),
        order_id=row['order_id'],
        executor_id=row['executor_id']
    )

    db.session.add(offer)


def add_order(row):
    order = Order(
        id=get_value(row, 'id'),
        name=row['name'],
        description=row['description'],
        start_date=row['start_date'],
        end_date=row['end_date'],
        address=row['address'],
        price=row['price'],
        customer_id=row['customer_id'],
        executor_id=row['executor_id'],
    )

    db.session.add(order)


def create_database():
    json_reader('./res/users.json', add_user)
    json_reader('./res/offers.json', add_offer)
    json_reader('./res/orders.json', add_order)
    db.session.commit()


def print_all_elements(rows, *fields):
    dump = json.dumps(
        serialize(
            rows,
            create_serialize_mapper('id', *fields)
        ),
        indent=4
    )

    return print_pre(dump)


def print_element(row, *fields):
    dump = json.dumps(
        create_serialize_mapper('id', *fields)(row),
        indent=4
    )

    return print_pre(dump)


def run():
    # Users

    # Отобразить всех пользователей
    @app.route('/users', methods=['GET'])
    def all_users_view():
        all_rows = User.query.all()
        return print_all_elements(all_rows, 'id', 'first_name', 'last_name')

    # Отобразить пользователя по id
    @app.route('/users/<int:user_id>', methods=['GET'])
    def user_view(user_id):
        user = User.query.get(user_id)
        return print_element(user, 'id', 'first_name', 'last_name')

    # Добавить пользователя
    @app.route('/users', methods=['POST'])
    def add_user_view():
        add_user(request.data)
        db.session.commit()
        return ''

    # Обновление пользователя по id
    @app.route('/users/<int:user_id>', methods=['PUT'])
    def put_user_view(user_id):
        add_user({id: user_id, **request.data})
        db.session.commit()
        return ''

    # Удаляем пользователя по id
    @app.route('/users/<int:user_id>', methods=['DELETE'])
    def delete_user_view(user_id):
        db.session.delete(User(id=user_id))
        db.session.commit()
        return ''

    # Offers

    # Отображаем все запросы
    @app.route('/offers')
    def all_offers_view():
        all_rows = Offer.query.all()
        return print_all_elements(all_rows, 'id', 'order_id', 'executor_id')

    # Отображаем запрос по id
    @app.route('/offers/<int:offer_id>')
    def offer_view(offer_id):
        offer = Offer.query.get(offer_id)
        return print_element(offer, 'id', 'order_id', 'executor_id')

    # Добавить запрос
    @app.route('/offers', methods=['POST'])
    def add_offer_view():
        add_offer(request.data)
        db.session.commit()
        return ''

    # Обновление запроса по id
    @app.route('/offers/<int:offer_id>', methods=['PUT'])
    def put_offer_view(offer_id):
        add_offer({id: offer_id, **request.data})
        db.session.commit()
        return ''

    # Удаляем запрос по id
    @app.route('/offers/<int:offer_id>', methods=['DELETE'])
    def delete_offer_view(offer_id):
        db.session.delete(Offer(id=offer_id))
        db.session.commit()
        return ''

    # Orders

    # Отобразить все заказы
    @app.route('/orders')
    def all_order_view():
        all_rows = Offer.query.all()
        return print_all_elements(all_rows, 'id', 'name', 'description')

    # Отобразить заказ по id
    @app.route('/orders/<int:offer_id>')
    def order_view(order_id):
        order = Offer.query.get(order_id)
        return print_element(order, 'id', 'name', 'description')

    # Добавить заказ
    @app.route('/orders', methods=['POST'])
    def add_order_view():
        add_offer(request.data)
        db.session.commit()
        return ''

    # Обновление заказа по id
    @app.route('/orders/<int:order_id>', methods=['PUT'])
    def put_order_view(order_id):
        add_order({id: order_id, **request.data})
        db.session.commit()
        return ''

    # Удаляем заказ по id
    @app.route('/orders/<int:order_id>', methods=['DELETE'])
    def delete_order_view(order_id):
        db.session.delete(Order(id=order_id))
        db.session.commit()
        return ''

    app.run(debug=True)


if __name__ == '__main__':

    if not has_exists:
        # Генерируем базу
        create_database()

    run()

