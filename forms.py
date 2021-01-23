from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, Form, validators
from wtforms.validators import DataRequired, Length, Email
from wtforms.fields.html5 import DateField

class ContactForm(FlaskForm):
  name = StringField("Name",validators=[DataRequired(),Length(min=2,max=150)])
  email = StringField("Email",validators=[DataRequired(),Email()])
  subject = StringField("Subject",validators=[DataRequired()])
  enquiries = TextAreaField("Enquiries ",validators=[DataRequired()])
  submit = SubmitField("Submit")

class FAQ(Form):
    question = StringField('Question', [validators.Length(min=1), validators.DataRequired()])
    answer = TextAreaField('Answer', [validators.Length(min=1), validators.DataRequired()])
    date = DateField('Date', [validators.DataRequired()], format='%Y-%m-%d')

class SearchBar(Form):
    search = StringField('')






