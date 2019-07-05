from boto.connection import AWSAuthConnection
from flask import Flask, render_template, request, redirect, url_for, flash
from models import Quiz, QuizForm
from datetime import datetime
from config import DevConfig
import json

application = Flask(__name__)
application.config.from_object(DevConfig)

class ESConnection(AWSAuthConnection):

	def __init__(self, region, **kwargs):
		super(ESConnection, self).__init__(**kwargs)
		self._set_auth_region_name(region)
		self._set_auth_service_name("es")

	def _required_auth_capability(self):
		return ['hmac-v4']

@application.before_first_request
def make_connect():
	global client
	# Note, boto receives credentials from the EC2 instance's IAM Role
	client = ESConnection(
		region='us-east-1',
		# Be sure to put the URL for your Elasticsearch endpoint below!
		host='search-test-domain-jxyhg5lk2ux3hzgh43ar2gbpde.us-east-1.es.amazonaws.com',
		is_secure=False)

@application.route('/', methods=['GET', 'POST'])
def take_test():
	form = QuizForm(request.form)
	if not form.validate_on_submit():
		return render_template('take_quiz.html', form=form)
	if request.method == 'POST':
		completed_quiz = Quiz(tags=['v0.1'])
		completed_quiz.essay_question = request.form.get('essay_question')
		completed_quiz.email_addr = request.form.get('email_addr')
		completed_quiz.iso_timestamp = datetime.now().isoformat()
		completed_quiz.client_ip_addr = request.remote_addr
		completed_quiz.is_spam = False

		esdata = completed_quiz.to_dict()
		headers = {'Content-Type':'application/json'}
		resp = client.make_request(method='POST',headers=headers,path='/big_survey/quiz',data=json.dumps(esdata))
		dict_resp = json.loads(resp.read())
		
		# print statements to check if index has been created in elasticsearch
		print(esdata)
		print(dict_resp)
		return 'Submitted!'

if __name__ == '__main__':
	application.run(host='0.0.0.0')