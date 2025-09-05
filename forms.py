from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField
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
    type = StringField('Treenityyppi', validators=[InputRequired()])
    duration = IntegerField('Kesto (min)', validators=[InputRequired()])
    description = TextAreaField('Kuvaus')
    submit = SubmitField('Lisää treeni')
