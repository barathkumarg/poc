from locust import HttpUser, task ,constant
from gevent.pool import Group

count = 0

class HelloWorldUser(HttpUser):
    host = "http://127.0.0.1:5000"
    wait_time = constant(1)
    url = '/root/function'

    @task
    def hello_world(self):
        self.client.get(self.url)
        global count
        count+=1
        print(count)