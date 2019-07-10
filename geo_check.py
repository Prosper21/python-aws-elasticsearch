from boto.connection import AWSAuthConnection

class ESConnection(AWSAuthConnection):

    def __init__(self, region, **kwargs):
        super(ESConnection, self).__init__(**kwargs)
        self._set_auth_region_name(region)
        self._set_auth_service_name("es")

    def _required_auth_capability(self):
        return ['hmac-v4']

if __name__ == "__main__":
    client = ESConnection(
            region='us-east-1',
            # Be sure to put the URL for your ElasticSearch endpoint below!
            host='search-test-domain-jxyhg5lk2ux3hzgh43ar2gbpde.us-east-1.es.amazonaws.com',
            is_secure=False)

    query = '{"query":{"filtered":{"filter":{"exists":{"field":"geo"}}}}}'
    headers = {'Content-Type':'application/json'}
    resp = client.make_request(method='GET',path='/big_survey/quiz/_search',headers=headers,data=query,params={"pretty":"true"})
    print resp.read()
