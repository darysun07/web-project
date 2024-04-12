import json
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user

import data
# from data.ctgry import Category
# from data.crt_prdct import CartsProduct
# from data.prdct import Product
# from data.cart import Cart
from data import db_session
from flask_forms.register import RegisterForm
from flask_forms.login_form import LoginForm
from data.users import User
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def load_product(name):
    with open(f'static/{str(name).capitalize()}.json', 'r', encoding='utf-8') as file:
        product = json.load(file)
    return product


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Wrong login or password", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/")
def index():
    categories = ['Помада', 'Тушь для ресниц', 'Пудра', 'Тени']
    return render_template("index.html", title='Главная', categories=categories)


@app.route("/<name_class>")
def name_class(name_class):
    product = load_product(name_class)
    return render_template('product.html', title=f'{str(name_class).capitalize()}',
                           name=f'{str(name_class).capitalize()}', product=product)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/cart')
def cart():
    return render_template("cart.html", title='Корзина')

# @app.route('/')
# def base():
#     db_sess = db_session.create_session()
#     res = db_sess.query(Category.Name).all()
#     categories = [category[0] for category in res]
#     return render_template('main.html', title='Главная страница', categories=categories)


#@app.route('/<Cate>', methods=['GET', 'POST'])
# def cat(Cate):
#     name = str(request.url).split('/')[-1]
#     db_sess = db_session.create_session()
#     if request.method == 'POST':
#         if flask_login.current_user.is_anonymous:
#             return redirect('/registration')
#         elif not flask_login.current_user.is_anonymous:
#             user = db_sess.query(User).filter(User.id == flask_login.current_user.id).first()
#             data.add_to_cart(user, int(request.form['add']))
#     ID = db_sess.query(Category.Id).filter(Category.Name == name).first()[0]
#     products = db_sess.query(Product.Name, Product.Price, Product.ImageId, Product.Id,
#                              Product.Count).filter(
#         Product.Category == int(ID)).all()
#     return render_template('category.html', title=f'{str(Cate).capitalize()}', products=products,
#                            cat=f'{str(Cate).capitalize()}')
#
#
# @app.route('/<Cate>/<int:prod>', methods=['GET', 'POST'])
# def prod(Cate, prod):
#     db_sess = db_session.create_session()
#     ID = int(str(request.url).split('/')[-1])
#     if request.form.get("add"):
#         if flask_login.current_user.is_anonymous:
#             return redirect('/registration')
#         elif not flask_login.current_user.is_anonymous:
#             user = db_sess.query(User).filter(User.id == flask_login.current_user.id).first()
#             data.add_to_cart(user, ID)
#     if request.form.get("delete"):
#         product = db_sess.query(Product).filter(Product.Id == ID).first()
#         img = db_sess.query(Product.ImageId).filter(Product.Id == ID).first()
#         try:
#             os.remove(f'./static/img/{img[0]}.jpg')
#         except Exception:
#             pass
#         db_sess.delete(product)
#         db_sess.commit()
#         return redirect(f'/{Cate}')
#     res = db_sess.query(Product.Name, Product.Price, Product.Description, Product.ImageId,
#                         Product.Count).filter(
#         Product.Id == ID).all()[0]
#     return render_template('product.html', title=res[0], product=res, Cate=Cate)
#
#
# @app.route('/cart')
# def cart():
#     global summ
#     summ = 0
#     db_sess = db_session.create_session()
#     res = db_sess.query(Cart.Id).filter(Cart.Owner == flask_login.current_user.id).first()
#     prdcts = db_sess.query(CartsProduct.ProductId, CartsProduct.Id).filter(
#         CartsProduct.OwnerCart == res[0]).all()
#     products = []
#     for prd in prdcts:
#         product = db_sess.query(Product).filter(Product.Id == prd[0]).first()
#         price = db_sess.query(Product.Price).filter(Product.Id == prd[0]).first()
#         summ += price[0]
#         ID = prd[1]
#         products.append([product, ID])
#     return render_template('cart.html', title='Коризна', products=products, summ=summ)
#
#
# @app.route('/payment', methods=['GET', 'POST'])
# def payment():
#     global summ
#     form = PaymentForm()
#     if request.method == 'POST':
#         db_sess = db_session.create_session()
#         owner = db_sess.query(Cart.Id).filter(Cart.Owner == flask_login.current_user.id).first()
#         res = db_sess.query(CartsProduct).filter(CartsProduct.OwnerCart == owner[0]).all()
#         for product in res:
#             db_sess.delete(product)
#             db_sess.commit()
#         summ = 0
#         return redirect('/success')
#     return render_template('payment.html', title='Оплата', form=form, summ=summ)


# @app.route('/success')
# def success():
#     return render_template('success.html', title='Hypewave')


@app.route('/profile')
def profile():
    return render_template("profile.html", title='Профиль')


@app.route('/abt')
def about():
    return render_template('abt.html', title='О компании')


@app.route('/dveloprs')
def developers():
    return render_template('dveloprs.html', title='Сайт')


def main():
    db_session.global_init("db/logged_users.sqlite")
    app.run()


if __name__ == '__main__':
    main()
