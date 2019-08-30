from flask_wtf import FlaskForm, RecaptchaField
from wtforms import TextField, SubmitField, TextAreaField
from wtforms.validators import Length, Email, DataRequired
from elasticsearch_dsl import DocType, Text, Boolean

#ElasticSearch ORM
class Quiz(DocType):
	essay_question = Text(analyzer='snowball')
	email_addr = Text(index='not_analyzed')
	iso_timestamp = Text(index='not_analyzed')
	client_ip_addr = Text(index='not_analyzed')
	is_spam = Boolean()
	class Meta:
		index = 'big_survey'


# Form ORM
class QuizForm(FlaskForm):
	essay_question = TextAreaField('Who do you think won the console wars of 1991, Sega Genesis or Super Nintendo? (2048 characters)', validators=[DataRequired(),Length(max=2047)])
	submit = SubmitField('Submit')
	email_addr = TextField('Enter Your Email', validators=[DataRequired(), Email()])
	recaptcha = RecaptchaField()
	submit = SubmitField('Submit')
