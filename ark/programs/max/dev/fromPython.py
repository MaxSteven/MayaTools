import os
import json

entity_type = "task"

responseDoc = open("c:/ie/response.json","w")
result = [{"name":"fer","id":"4","description":"testing 4"},\
            {"name":"eght ","id":"8","description":"testing 8"},\
            {"name":"f sa","id":"5","description":"testing 5"},\
            {"name":"twe","id":"12","description":"testing 12"}]
responseDoc.write(json.dumps(result))
responseDoc.close()
