import requests
import json
from pprint import pprint

r = requests.post("https://a.febijo.de/node/gettoken",
                  data={'nutzer': 'chris', 'passwd': '1'})
print(r.status_code, r.reason)
decoded = json.loads(r.text)
pprint (decoded)
auth = decoded["token"]
print auth
