#!/usr/bin/python3

import requests
from requests.auth import HTTPBasicAuth
import json
import sys
from cloudsecrets.gcp import Secrets
import time

env = "stage"
if len(sys.argv) > 1:
  env = sys.argv[1]

creds = Secrets("jira-sysadmin-creds")
creds = json.loads(dict(creds)[env])

user = creds['user']
password = creds['password']
url_base = creds['url_base']

headers = { 'Content-Type': 'application/json' }

res = requests.get(f"{url_base}/cluster/nodes", headers=headers, auth=HTTPBasicAuth(user,password))
nodes = json.loads(res.text)

for n in nodes:
  nodeId = n['nodeId']
  alive = n['alive']
  state = n['state']
  if not alive:
    if state == 'ACTIVE':
      print(f"Node {nodeId} is active but dead, marking offline.")
      requests.put(f"{url_base}/cluster/node/{nodeId}/offline",headers=headers,auth=HTTPBasicAuth(user,password))
      nodes += [n]
      time.sleep(2)
    elif state == 'OFFLINE':
      print(f"Node {nodeId} is offline but still in the cluster, removing.")
      requests.delete(f"{url_base}/cluster/node/{nodeId}",headers=headers,auth=HTTPBasicAuth(user,password))
    else:
      print(f"Node {nodeId} is offline and still in the cluster, and in a weird state, so not touching.")
  else:
    print(f"Node {nodeId} is online and doing great")

