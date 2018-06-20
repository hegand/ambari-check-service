import json

class PayloadTemplate(object):
    def __init__(self, service_name):
        self.payload = '' + \
        '{' + \
        '  "RequestInfo":{' + \
        '      "context":"{0} Service Check",'.format(service_name) + \
        '      "command":"{0}_SERVICE_CHECK"'.format("ZOOKEEPER_QUORUM" if service_name == "ZOOKEEPER" else service_name) + \
        '   },' + \
        '   "Requests/resource_filters":[' + \
        '      {' + \
        '         "service_name":"{0}"'.format(service_name) + \
        '      }' + \
        '   ]' + \
        '}'

    def get(self):
        return self.payload

    def get_json(self):
        return json.loads(self.payload)

class PayloadBatchTemplate(object):
    def __init__(self, cluster_name, service_name_list):
        requests = ['' + \
        '{' + \
        '  "order_id":{0},'.format(service_name_list.index(service_name)) + \
        '  "type":"POST",' + \
        '  "uri":"/api/v1/clusters/{0}/requests",'.format(cluster_name) + \
        '  "RequestBodyInfo":' + \
        PayloadTemplate(service_name).get() +
        '}' for service_name in service_name_list]
        self.payload = '' + \
        '{' + \
        '"RequestSchedule":{' + \
        '  "batch":[' + \
        '      {' + \
        '         "requests":[' + \
        ','.join(requests) + \
        '         ]' + \
        '      },' + \
        '      {' + \
        '        "batch_settings":{' + \
        '          "batch_separation_in_seconds":1,' + \
        '          "task_failure_tolerance":0' + \
        '        }' + \
        '      }' + \
        '    ]' + \
        '  }' + \
        '}'

    def get(self):
        return self.payload

    def get_json(self):
        return json.loads(self.payload)
