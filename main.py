import json, flask_login
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_forms.payment import PaymentForm

# import data
# from data.ctgry import Category
# from data.crt_prdct import CartsProduct
# from data.prdct import Product
# from data.cart import Cart

from data import db_session
from flask_forms.register import RegisterForm
from flask_forms.login_form import LoginForm
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

cart_prods = {}
summ = 0


def add_to_cart(user, product):
    global cart_prods, summ
    print(product.split()[0].lower())
    with open(f'static/{product.split()[0].lower()}.json', encoding='utf-8') as f:
        data = json.load(f)
        for i in data:
            if i["name"] == product:
                cost = i["description"]
                summ += int(cost)
    #print(summ)
    if user not in cart_prods:
        cart_prods[user] = [f'{product} - {cost}р\n']
    else:
        cart_prods[user].append(f'{product} - {cost}р\n')
    with open('static/cart.json', 'w', encoding='utf-8') as file:
        json.dump(cart_prods, file)


def load_product(name_class):
    with open(f'static/{str(name_class).capitalize()}.json', 'r', encoding='utf-8') as file:
        product = json.load(file)
        return product


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    categories = ['Помада', 'Тушь', 'Пудра', 'Тени']
    return render_template("index.html", title='Главная', categories=categories)


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
        return render_template('login.html', message="Невереный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/<name_class>", methods=['GET', 'POST'])
def name_class(name_class):
    db_sess = db_session.create_session()
    if request.method == 'POST':
        if not flask_login.current_user.is_authenticated:
            print(1)
            return redirect("/login")
        elif flask_login.current_user.is_authenticated:
            user = flask_login.current_user.name
            add_to_cart(user, request.form['add'])
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
    global summ
    if not flask_login.current_user.is_authenticated:
        return redirect("/login")
    with open('static/cart.json', encoding='utf-8') as file:
        data = json.load(file)
        prod = ''.join(data[flask_login.current_user.name])
    return render_template("cart.html", title='Корзина', prod=prod, summ=summ)


#@app.route('/delete/<product>')
#def delete_c_p(product):
    #global summ
    # db_sess = db_session.create_session()
    # res = db_sess.query(CartsProduct).filter(CartsProduct.Id == product).first()
    # db_sess.delete(res)
    # db_sess.commit()
    #summ = 0
    #return redirect('/cart')


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    form = PaymentForm()
    if request.method == 'POST':
        return redirect('/finish')
    return render_template('payment.html', title='Оплата', form=form, summ=summ)


@app.route('/finish')
def finish():
    global summ
    summ = 0
    #with open('static/cart.json', 'w', encoding='utf-8') as f:
    return render_template('finish.html', title='Оплачено')


@app.route('/profile')
def profile():
    return render_template("profile.html", title='Профиль')


@app.route('/abt')
def about():
    return render_template('abt.html', title='О компании')


@app.route('/dveloprs')
def developers():
    return render_template('dveloprs.html', title='Сайтик')


def main():
    db_session.global_init("db/logged_users.sqlite")
    app.run()


if __name__ == '__main__':
    main()
