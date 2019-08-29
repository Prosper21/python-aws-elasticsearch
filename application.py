from boto.connection import AWSAuthConnection
from flask import Flask, render_template, request, redirect, url_for, flash
from models import Quiz, QuizForm
from datetime import datetime
from config import ProdConfig, CeleryConfig, AWSConfig
import json
from gevent.pywsgi import WSGIServer


# Use bootstrap for better looking forms
from flask_bootstrap import Bootstrap

# celery for asynchronous tasks
from celery import Celery

from tasks import get_location

def make_celery(application):
	celery = Celery(application.import_name, broker=application.config['broker_url'])
	celery.conf.update(application.config)
	TaskBase = celery.Task
	class ContextTask(TaskBase):
		abstract = True
		def __call__(self, *args, **kwargs):
			with application.app_context():
				return TaskBase.__call__(self, *args, **kwargs)
	celery.Task = ContextTask
	return celery

application = Flask(__name__)
application.config.from_object(ProdConfig)
application.config.update(broker_url=CeleryConfig.broker_url)

Bootstrap(application)

# Wrap the bootstrapped application in celery
celery = make_celery(application)

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
		aws_access_key_id=AWSConfig.aws_access_key_id,
		aws_secret_access_key=AWSConfig.aws_secret_access_key,
		is_secure=False)

def flash_errors(form):
	for field, errors in form.errors.items():
		for error in errors:
			flash(u"%s - %s" % (
				getattr(form, field).label.text,
				error
			))

@application.route('/', methods=['GET', 'POST'])
def take_test():
	form = QuizForm(request.form)
	if not form.validate_on_submit():
		flash_errors(form)
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
		flash('Survey sbmitted!')

		# The asynch task
		#get_location.delay(dict_resp['_id'],completed_quiz.client_ip_addr)
		get_location.delay(dict_resp['_id'],'154.226.175.219')	# had to use my ip address otherwise it defaults to '127.0.0.1'
		
		# Asych task complete
		return 'Thank You!'


if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	host = '0.0.0.0'
	http_server = WSGIServer((host, port), application)
	print("Starting server on port {}".format(port))
	http_server.serve_forever()
