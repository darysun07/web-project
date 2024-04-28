from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField
from wtforms.validators import DataRequired, InputRequired, NumberRange


class PaymentForm(FlaskForm):
    card = IntegerField('Номер карты', validators=[InputRequired()])
    name_recipient = StringField('Имя получателя', validators=[DataRequired()])
    address = StringField('Адрес доставки', validators=[DataRequired()])
    submit = SubmitField('Оплатить')
