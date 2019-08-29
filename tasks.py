from boto.connection import AWSAuthConnection
import requests
from celery import Celery
from config import CeleryConfig, AWSConfig

application = Celery('tasks')
application.config_from_object(CeleryConfig)

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
    aws_access_key_id=AWSConfig.aws_access_key_id,
    aws_secret_access_key=AWSConfig.aws_secret_access_key,
    is_secure=False)

@application.task
def get_location(user,address):
    # Get the location from the API
    r = requests.get('http://api.ipstack.com/' + address + '?access_key=d4eaa48fbaa2ade3f8d90e03d1d2d7ae')
    print(r.json())
    jstr = str(r.json()['latitude']) + ',' + str(r.json()['longitude'])
    # Update the ElasticSearch index
    headers = {'Content-Type':'application/json'}
    resp = client.make_request(method='POST',path='/big_survey/quiz/' + user + '/_update',headers=headers,data='{"doc":{"geo":"' + jstr + '"}}')
    return