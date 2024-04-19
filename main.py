import json, flask_login
import os.path
from flask import Flask, render_template, redirect, request, flash
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


def add_to_cart(name_user, product):
    global cart_prods#, summ
    print(product.split()[0].lower())
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == flask_login.current_user.name).first()
    #print(user)
    with open(f'static/{product.split()[0].lower()}.json', encoding='utf-8') as f:
        data = json.load(f)
        for i in data:
            if i["name"] == product:
                cost = i["description"]
                if user:
                    user.sum_pr += int(cost)
                #summ += int(cost)
    db_sess.commit()
    #db_sess.refresh(user)
    print(user.sum_pr)
    if name_user not in cart_prods:
        cart_prods[name_user] = [f'{product} - {cost}р']
    else:
        cart_prods[name_user].append(f'{product} - {cost}р')
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
    categories = ['Помада', 'Тушь', 'Пудра', 'Тени', 'Парфюм']
    return render_template("index.html", title='Главная', categories=categories)


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


@app.route("/<name_class>", methods=['GET', 'POST'])
def name_class(name_class):
    if request.method == 'POST':
        if not flask_login.current_user.is_authenticated:
            return redirect("/login")
        elif flask_login.current_user.is_authenticated:
            name_user = flask_login.current_user.name
            add_to_cart(name_user, request.form['add'])
            #flash('Товар добавлен в корзину')
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
    #global summ
    if not flask_login.current_user.is_authenticated:
        return redirect("/login")
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == flask_login.current_user.name).first()
    summ = user.sum_pr
    with open('static/cart.json', encoding='utf-8') as file:
        data = json.load(file)
        if flask_login.current_user.name not in data:
            prod = []
        else:
            prod = data[flask_login.current_user.name]
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
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == flask_login.current_user.name).first()
    summ = user.sum_pr
    form = PaymentForm()
    if request.method == 'POST':
        return redirect('/finish')
    return render_template('payment.html', title='Оплата', form=form, summ=summ)


@app.route('/finish')
def finish():
    #global summ
    summ = 0
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == flask_login.current_user.name).first()
    user.sum_pr = 0
    db_sess.commit()
    with open('static/cart.json', encoding='utf-8') as f:
        data = json.load(f)
        f.close()
    if os.path.isfile(f'customers/{flask_login.current_user.id}.txt'):
        with open(f'customers/{flask_login.current_user.id}.txt', 'a', encoding='utf-8') as txt_file:
            txt_file.write('\n'.join(data[flask_login.current_user.name]) + '\n')
            print(1)
            txt_file.close()
    else:
        with open(f'customers/{flask_login.current_user.id}.txt', 'w', encoding='utf-8') as txt_file:
            txt_file.write('\n'.join(data[flask_login.current_user.name]))
            print(2)
            txt_file.close()
    data[flask_login.current_user.name] = []
    with open('static/cart.json', 'w', encoding='utf-8') as f:
        json.dump(data, f)
    return render_template('finish.html', title='Оплачено')


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
    return redirect('/')


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
