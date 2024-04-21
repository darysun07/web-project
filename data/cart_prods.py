import sqlalchemy

from .db_session import SqlAlchemyBase


class CartProd(SqlAlchemyBase):
    __tablename__ = 'cart_prods'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    profile = sqlalchemy.Column(sqlalchemy.String, nullable=True)
