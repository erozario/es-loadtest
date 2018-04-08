from locust import HttpLocust, TaskSet, task, events
import time
from elasticsearch import Elasticsearch, helpers
from os import listdir, path
import json
from hashlib import md5

def read_json(file_path):
    with open(path.abspath(path.join(path.dirname(__file__),'loadfiles',file_path))) as raw_json:
        return json.load(raw_json)

def read_id(file_path):
    return read_json(file_path).get('_id')

def read_source(file_path):
    source = read_json(file_path)
    source.pop('_id')
    return source

class loadInsert(TaskSet):
    def __init__(self, *args, **kwargs):
        super(loadInsert, self).__init__(*args, **kwargs)
        self.search_engine = Elasticsearch(["elasticsearch.local"])

    @task(100)
    def bulk_insert(self):
        start_time = time.time()
        try:
            actions = [
              {
                "_index": "logstash-2015.05.20",
                "_type": "log",
                "_id": read_id(file),
                "_source": read_source(file)
              }
              for file in listdir(path.abspath(path.join(path.dirname(__file__),'loadfiles'))) 
                if file.endswith('.json')
            ]
            result = helpers.bulk(self.search_engine, actions)
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type='POST',
                                        name='Insert',
                                        response_time=total_time,
                                        exception=e)
        else:   
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(request_type='POST',
                                        name='Insert',
                                        response_time=total_time,
                                        response_length=len(result))

class reader(TaskSet):
    def __init__(self, *args, **kwargs):
        super(reader, self).__init__(*args, **kwargs)
        self.search_engine = Elasticsearch(["elasticsearch.local"])

    @task(3)
    def get_must(self):
        start_time = time.time()
        try:
            result = self.search_engine.search(
                index='logstash-2015.05.20',
                doc_type='log',
                body={
                  "query": {
                    "bool": {
                      "must": [
                        { "match": { "response": "200" } }
                      ]
                    }
                  }
                }
            )
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type='GET',
                                        name='Search response 200',
                                        response_time=total_time,
                                        exception=e)
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(request_type='GET',
                                        name='Search response 200',
                                        response_time=total_time,
                                        response_length=len(result))


    @task(5)
    def get_wildcard(self):
        start_time = time.time()
        try:
            result = self.search_engine.search(
                index='logstash-2015.05.20',
                doc_type='log',
                body={
                  "query": {
                    "bool": {
                      "should": [
                        { "wildcard": { "response": "*" } }
                      ]
                    }
                  }
                }
            )
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type='GET',
                                        name='Search response *',
                                        response_time=total_time,
                                        exception=e)
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(request_type='GET',
                                        name='Search response *',
                                        response_time=total_time,
                                        response_length=len(result))


class LocustLoadInput(HttpLocust):
    task_set = loadInsert
    min_wait = 2000
    max_wait = 60000

class LocustLoadOutput(HttpLocust):
    task_set = reader
    min_wait = 2000
    max_wait = 30000
