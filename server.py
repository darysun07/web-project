# импорт необходимых библиотек
import json
import flask_login
import os.path
from transliterate import translit
from flask import Flask, render_template, redirect, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_forms.payment import PaymentForm

from data import db_session
from flask_forms.register import RegisterForm
from flask_forms.login_form import LoginForm
from data.users import User
from data.cart_prods import CartProd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


# функция добавления в корзину;
# загрузка товара, добавленного в корзину пользователем, из файла-json(категории), добавление товара в таблицу CartProd;
# подсчет суммы
def add_to_cart(product):
    db_sess = db_session.create_session()
    name_file = translit(product.split()[0].lower(), 'ru', reversed=True)
    user = db_sess.query(User).filter(User.name == flask_login.current_user.name).first()
    with open(f'static/{name_file}.json', encoding='utf-8') as f:
        data = json.load(f)
        for i in data:
            if i["name"] == product:
                cost = i["description"]
                if user:
                    user.sum_pr += int(cost)
                    cart_pr = CartProd(name=i["name"],
                                       cost=int(cost),
                                       profile=flask_login.current_user.id)
    db_sess.add(cart_pr)
    db_sess.commit()


# загрузка товаров нужной категории из json-файла
def load_product(name_cat):
    with open(f'static/{str(name_cat)}.json', 'r', encoding='utf-8') as file:
        product = json.load(file)
        return product


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# главная страница
@app.route("/")
def index():
    if not os.path.isdir("customers"):
        os.mkdir("customers")
    categories = {"Помада": "pomada", "Тушь": "tush'", "Пудра": "pudra", "Тени": "teni", "Парфюм": "parfjum"}
    return render_template("index.html", title='Главная', categories=categories)


# регистрация пользователя
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="! Пароли не совпадают !")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="! Такой пользователь уже есть !")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            email=form.email.data,
            sum_pr=0
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


# авторизация пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="! Невереный логин или пароль !", form=form)
    return render_template('login.html', title='Авторизация', form=form)


# выход пользователя из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# страница категории товаров
@app.route("/<name_cat>", methods=['GET', 'POST'])
def name_class(name_cat):
    if request.method == 'POST':
        if not flask_login.current_user.is_authenticated:
            return redirect("/login")
        elif flask_login.current_user.is_authenticated:
            add_to_cart(request.form['add'])
    product = load_product(name_cat)
    return render_template('product.html', title=str(name_cat).capitalize(),
                           name=str(translit(name_cat, "ru")).capitalize(), product=product)


# страница корзины
@app.route('/cart')
def cart():
    if not flask_login.current_user.is_authenticated:
        return redirect("/login")
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == flask_login.current_user.name).first()
    cart_prod = db_sess.query(CartProd.name, CartProd.cost).filter(
        CartProd.profile == flask_login.current_user.id).all()
    prods = []
    for i in cart_prod:
        prods.append(f'{i[0]} - {i[1]}р')
    summ = user.sum_pr
    return render_template("cart.html", title='Корзина', prod=prods, summ=summ)


# страница оплаты
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == flask_login.current_user.name).first()
    summ = user.sum_pr
    form = PaymentForm()
    if request.method == 'POST':
        card = str(request.form.get('card')).replace(' ', '')
        if len(card) != 16 or not card.isdigit():
            flash('! Неверный формат ввода карты !')
        else:
            return redirect('/finish')
    return render_template('payment.html', title='Оплата', form=form, summ=summ)


# страница успешной оплаты заказа; добавление купленных товаров в файл json, создающийся с именем id пользователя
@app.route('/finish')
def finish():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == flask_login.current_user.name).first()
    user.sum_pr = 0
    cart_pr2 = db_sess.query(CartProd.name, CartProd.cost).filter(CartProd.profile == flask_login.current_user.id).all()
    data = []
    for i in cart_pr2:
        data.append(f'{i[0]}-{i[1]}р')
    if os.path.isfile(f'customers/{flask_login.current_user.id}.txt'):
        with open(f'customers/{flask_login.current_user.id}.txt', 'a', encoding='utf-8') as txt_file:
            txt_file.write('\n'.join(data) + '\n')
    else:
        with open(f'customers/{flask_login.current_user.id}.txt', 'w', encoding='utf-8') as txt_file:
            txt_file.write('\n'.join(data) + '\n')
    cart_pr = CartProd.__table__.delete().where(CartProd.profile == flask_login.current_user.id)
    db_sess.execute(cart_pr)
    db_sess.commit()
    return render_template('finish.html', title='Оплачено')


# страница профиля; загрузка из файла json купленных товаров - истории заказов
@app.route('/profile')
def profile():
    if os.path.isfile(f'customers/{flask_login.current_user.id}.txt'):
        with open(f'customers/{flask_login.current_user.id}.txt', 'r', encoding='utf-8') as file:
            orders = file.readlines()
    else:
        orders = ['Вы еще ничего не приобрели в нашем магазине']
    return render_template("profile.html", title='Профиль', orders=orders)


@login_required
@app.route('/profile_del', methods=['GET', 'POST'])
def delete_profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == flask_login.current_user.id).first()
    db_sess.delete(user)
    db_sess.commit()
    if os.path.isfile(f'customers/{flask_login.current_user.id}.txt'):
        os.remove(f'customers/{flask_login.current_user.id}.txt')
    return redirect('/')


@app.route('/dveloprs')
def developers():
    return render_template('dveloprs.html', title='Сайтик')


def main():
    if not os.path.isdir("db"):
        os.mkdir("db")
    db_session.global_init("db/logged_users.sqlite")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
