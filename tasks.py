from boto.connection import AWSAuthConnection
import requests
from celery import Celery

# Be sure to add your SQS URL below!
application = Celery('tasks',broker='sqs://sqs.us-east-1.amazonaws.com/169639297394/flask-es')

class ESConnection(AWSAuthConnection):
    def __init__(self, region, **kwargs):
        super(ESConnection, self).__init__(**kwargs)
        self._set_auth_region_name(region)
        self._set_auth_service_name("es")
    def _required_auth_capability(self):
        return ['hmac-v4']

client = ESConnection(
      region='us-east-1',
      host='search-test-domain-jxyhg5lk2ux3hzgh43ar2gbpde.us-east-1.es.amazonaws.com',
      is_secure=False)

@application.task
def get_location(user,address):
        # Get the location from the API
        r = requests.get('http://freegeoip.net/json/' + address)
        jstr = str(r.json()['latitude']) + ',' + str(r.json()['longitude'])
        # Update the ElasticSearch index
        headers = {'Content-Type':'application/json'}
        resp = client.make_request(method='POST',path='/big_survey/quiz/' + user + '/_update',headers=headers,data='{"doc":{"geo":"' + jstr + '"}}')
        return