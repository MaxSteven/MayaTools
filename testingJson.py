import json

jsonInfo = {
			"1": "A",
			"2": "B",
			"3": 
				{
					"X":"a",
					"Y": "b"
				}
			}

file = "C:\\GitHub\\jsonTest.json"

with open(file, 'a') as f:
	json.dump(jsonInfo, f, indent = 2)

