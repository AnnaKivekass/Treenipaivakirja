from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class EditMessageForm(FlaskForm):
    title = StringField("Otsikko", validators=[DataRequired(), Length(max=200)])
    content = TextAreaField("Sisältö", validators=[DataRequired(), Length(max=5000)])
    submit = SubmitField("Tallenna")
