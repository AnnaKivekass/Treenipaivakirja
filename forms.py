from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length

class RegisterForm(FlaskForm):
    username = StringField('Käyttäjätunnus', validators=[InputRequired(), Length(min=4, max=50)])
    password = PasswordField('Salasana', validators=[InputRequired(), Length(min=4, max=50)])
    submit = SubmitField('Rekisteröidy')

class LoginForm(FlaskForm):
    username = StringField('Käyttäjätunnus', validators=[InputRequired()])
    password = PasswordField('Salasana', validators=[InputRequired()])
    submit = SubmitField('Kirjaudu')

class WorkoutForm(FlaskForm):
    date = StringField('Päivämäärä', validators=[InputRequired()])
    type = SelectField('Treenityyppi', choices=[
        ('juoksu', 'Juoksu'),
        ('pyöräily', 'Pyöräily'),
        ('uinti', 'Uinti'),
        ('kävely', 'Kävely'),
        ('kuntosali', 'Kuntosali'),
        ('jooga', 'Jooga')
    ], validators=[InputRequired()])
    duration = IntegerField('Kesto (min)', validators=[InputRequired()])
    description = TextAreaField('Kuvaus')
    submit = SubmitField('Lisää treeni')

class MessageForm(FlaskForm):
    content = TextAreaField('Viestin sisältö', validators=[InputRequired()])
    submit = SubmitField('Lähetä viesti')
