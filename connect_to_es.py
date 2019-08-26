from boto.connection import AWSAuthConnection
from config import AWSConfig

class ESConnection(AWSAuthConnection):

	def __init__(self, region, **kwargs):
		super(ESConnection, self).__init__(**kwargs)
		self._set_auth_region_name(region)
		self._set_auth_service_name("es")

	def _required_auth_capability(self):
		return ['hmac-v4']

if __name__ == "__main__":
	client = ESConnection(
		aws_access_key_id=AWSConfig.aws_access_key_id,
    	aws_secret_access_key=AWSConfig.aws_secret_access_key,
		region='us-east-1',
		# Be sure to put the URL for your Elasticsearch endpoint below!
		host='search-test-domain-jxyhg5lk2ux3hzgh43ar2gbpde.us-east-1.es.amazonaws.com',
		is_secure=False)

	headers = {'Content-Type':'application/json'}
	resp = client.make_request(method='POST',headers=headers,path='/big_survey/quiz/_search',data='{ "query" : { "match_all" : { } } }')
	print(resp.read())
