"""
HTTP client simulator. It simulate a number of concurrent users and calculate the response time for each request.
"""

import requests
import time
import threading
import sys
from requests.exceptions import ConnectionError

if len(sys.argv) < 4:
  print('To few arguments; you need to specify 3 arguments.')
  print('Default values will be used for server_ip, no of users and think time.\n')
  swarm_master_ip = '10.1.0.138'  # ip address of the Swarm master node
  no_users = 1  # number of concurrent users sending request to the server
  think_time = 1  # the user think time (seconds) in between consequent requests
else:
  print('Default values have be overwritten.')
  swarm_master_ip = sys.argv[1]
  no_users = int(sys.argv[2])
  think_time = float(sys.argv[3])

class MyThread(threading.Thread):
  def __init__(self, name, counter):
    threading.Thread.__init__(self)
    self.threadID = counter
    self.name = name
    self.counter = counter

  def run(self):
    print("Starting " + self.name + str(self.counter))
    workload(self.name + str(self.counter))


def workload(user):
  while True:
    t0 = time.time()
    try:
      r = requests.get('http://' + swarm_master_ip + ':8000/')
      t1 = time.time()
      time.sleep(think_time)
      print("Response Time for " + user + " = " + str(t1 - t0))
      payload = {'time': str(t1-t0)}
      try:
        # post just to get graph values
        response = requests.post('http://' + swarm_master_ip  + ':1337/metric', data=payload)
      except ConnectionError as e:
        print ('Metric for autoscaler is down')
    except ConnectionError as e:
      print ('Service is autoscaling. Please try again')

if __name__ == "__main__":
  threads = []
  for i in range(no_users):
    threads.append(MyThread("User", i))

  for i in range(no_users):
    threads[i].start()

  for i in range(no_users):
    threads[i].join()
