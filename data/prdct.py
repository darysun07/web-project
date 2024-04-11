import sqlalchemy
from data.db_session import SqlAlchemyBase


class Product(SqlAlchemyBase):
    __tablename__ = 'Prdct'

    Id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    Name = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=False)

    Description = sqlalchemy.Column(sqlalchemy.String)

    Price = sqlalchemy.Column(sqlalchemy.REAL)

    Count = sqlalchemy.Column(sqlalchemy.Integer)

    ImgId = sqlalchemy.Column(sqlalchemy.Integer)

    Ctgry = sqlalchemy.Column(sqlalchemy.Integer)
