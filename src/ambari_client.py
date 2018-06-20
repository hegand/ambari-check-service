import urllib2,json

from ambari_service_check_payload_template import PayloadTemplate, PayloadBatchTemplate
from ambari_error import AmbariError


class AmbariClient(object):
    def __init__(self,hostname,port,cluster_name,creds,ssl=False):
        self.hostname = hostname
        self.port = port
        self.cluster_name = cluster_name
        self.creds = creds
        self.base_url = "http{0}://{1}:{2}/api/v1/clusters/{3}/".format("s" if ssl else "", self.hostname, self.port, self.cluster_name)
        self.test_base_url()

    def test_base_url(self):
        url = self.base_url[:-len(self.cluster_name)-1]
        data = self.get(url)
        try:
            cluster_names = map(lambda x: x["Clusters"]["cluster_name"], data["items"])
            if self.cluster_name in cluster_names:
                return
            else:
                raise AmbariError("This cluster ({0}) is not managed by this ambari instance ({1}:{2})".format(self.cluster_name,self.hostname,str(self.port)))
        except KeyError as e:
            raise AmbariError("Server response is not valid or empty, please check")

    def request(self, url, data):
        request = urllib2.Request(url, data, {"X-Requested-By": "ambari", "Authorization": "Basic {0}".format(self.creds)})
        try:
          connection = urllib2.urlopen(request)
          return json.loads(connection.read())
        except urllib2.HTTPError as e:
          if e.code >= 400:
            raise AmbariError(json.loads(e.read())["message"])
        except urllib2.URLError as e:
            raise AmbariError("Please check the url, {0} is not valid or the server is not responding. {1}".format(url,e.reason))

    def get(self,url):
        return self.request(url, None)

    def post(self, url, data):
        return self.request(url, data)

    def get_service_list(self):
        url = self.base_url + "services/"
        resp = self.get(url)
        try:
            return map(lambda x: x["ServiceInfo"]["service_name"], resp["items"])
        except KeyError as e:
            raise AmbariError("Server response is not valid or empty, please check")

    def check_service(self, service_name):
        if service_name in self.get_service_list():
            url = self.base_url + "requests/"
            payload = PayloadTemplate(service_name).get()
            return self.post(url, payload)
        else:
            raise AmbariError("{0} service is not installed on {1} cluster".format(service_name, self.cluster_name))

    def check_service_batch(self, service_name_list):
        service_name_list_global = self.get_service_list()
        not_in = [service for service in service_name_list if service not in service_name_list_global]
        if len(not_in) == len(service_name_list):
            raise AmbariError("Neither of the services ({0}) are installed on this cluster".format(', '.join(not_in)))
        elif not_in:
            print("Some services ({0}) are not installed on this cluster".format(', '.join(not_in)))
        else:
            url = self.base_url + "request_schedules/"
            payload = PayloadBatchTemplate(self.cluster_name,[service_name for service_name in service_name_list if service_name not in not_in]).get()
            return self.post(url, payload)

    def check_batch_job_status(self, id):
        url = self.base_url + "request_schedules/{0}".format(str(id))
        try:
            resp = self.get(url)["RequestSchedule"]["status"]
            return resp
        except KeyError as e:
            raise AmbariError("Server response is not valid or empty, please check")

    def check_batch_job(self, id):
        url = self.base_url + "request_schedules/{0}".format(str(id))
        try:
            resp = [{u"service_name": json.loads(req["request_body"])["Requests/resource_filters"][0]["service_name"], u"status": req["request_status"]} for req in self.get(url)["RequestSchedule"]["batch"]["batch_requests"]]
            return resp
        except KeyError as e:
            raise AmbariError("Server response is not valid or empty, please check")

    def check_request_status(self, id):
        url = self.base_url + "requests/{0}".format(str(id))
        try:
            resp = self.get(url)["Requests"]["request_status"]
            return resp
        except KeyError as e:
            raise AmbariError("Server response is not valid or empty, please check")
