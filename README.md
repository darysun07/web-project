# Проект WEB: интернет-магазин "PODASH"

### Выполнили: Соколенко Дарья и Краснопольская Полина

---

Проект представляет собой интернет-магазин с товарами из разных категорий косметики. Для покупки товаров пользователю нужно будет пройти регистрацию. 

#### Страницы сайта:

- Главная страница с выбором категорий
- Регистрация
- Вход
- Профиль с историей заказов
- Корзина товаров
- Оформление заказа
- Оплата заказа
- Успешное оформление заказа

---

#### Описание работы программы:

- Главная страница (“/”) является основной в приложении. Здесь расположены категории товаров, краткий свод информации
про магазин и ссылка на разработчиков. В каждой категории есть соответствующие товары, которые можно добавить в 
корзину, но при добавлении нужного товара программа запрашивает авторизацию. 
- Регистрация (“/register”) обязательна для новых пользователей сайта. Здесь пользователь вводит свои имя и фамилию,
а также почту, пароль (с проверкой) и возраст. Если пользователь уже был зарегистрирован программа укажет на это.
- После регистрации пользователя перекинет на страницу входа (“/login”). Здесь нужно повторно ввести свои почту и 
пароль. После этого пользователь возвращается на главную страницу.
- Перейдя в профиль (“/profile”) можно увидеть информацию о пользователе, его логин и возраст. Есть возможность выхода 
из аккаунта и его удаление. Также есть история заказов, связанная с его историей покупок в данном магазине.
- При выборе покупки пользователь добавляет выбранные товары в корзину, после чего они попадают в корзину (“/cart”).
В корзине товаров есть список товаров, выбранных пользователем, и кнопка оплатить.
- Во время оплаты(“/payment”) пользователь вводит номер карты, имя получателя товара и адрес доставки.
При неправильно введенном номере карты программа сообщает об этом.
- После успешной оплаты товаров появляется страница (“/finish”) с комментарием об успешном заказе продукции.
В профиле пользователя появляется история заказанных товаров.

---

#### Категории товаров: 

- Помада
- Тушь
- Пудра
- Тени
- Парфюм

---

#### Регистрация:

- email
- пароль
- подтверждение пароля
- имя пользователя
- фамилия пользователя
- возраст пользователя

Для входа нужно будет ввести email и пароль

---

#### Использование базы данных: 

- хранение данных зарегестрировшихся пользователей и общую сумму всех товаров, добавленных в корзину этим пользователем
- хранение данных товаров, добавленных в корзину авторизовавшимся пользователем

---

#### Классы и их назначение:

- customers - папка с покупками пользователей программы (у каждого собственная история покупок)
- data - папка с созданием баз данных SQLalchemy по товарам и пользователям (и её подсоединению к самой программе)
- db - папка с базой данных зарегистрированных пользователей
- flask_forms - папка с формами для страниц авторизации, регистрации и оплаты
- static - папка с нужными изображениями товаров и шрифтом для названия фирмы магазина в программе
- templates - шаблоны для страниц программы на WEB

---

#### Использованные технологии:

- язык программирования: Python
- фреймворк: Flask
- фронтенд: HTML, CSS
- база данных: SQLAlchemy
- работа с файлами: OS
- хранение данных товаров по категориям, использование этих данных: json
- transliterate для корректной работы страниц сайта
