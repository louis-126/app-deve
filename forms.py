from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class ContactForm(FlaskForm):
  name = StringField("Name",validators=[DataRequired(),Length(min=2,max=150)])
  email = StringField("Email",validators=[DataRequired(),Email()])
  subject = StringField("Subject",validators=[DataRequired()])
  enquiries = TextAreaField("Enquiries ",validators=[DataRequired()])
  submit = SubmitField("Submit")









