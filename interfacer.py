import csv
import json

csvPath = './Aircraft Performance-Grid view.csv'
jsonPath = './aircraft-performances.json'

data = {}

with open(csvPath, encoding='utf-8') as csvf:
    csvReader = csv.DictReader(csvf)
    for rows in csvReader:
        key = rows["Airplane"]
        data[key] = rows
keys_array = []
keys = data.keys()
for key in keys:
    keys_array.append(key)
    obj = data[key]
    data[key]["VS"] = "Vertical speed : GS * 5"
    del obj["\ufeffBrand"]
    del obj["Picture"]
    del obj["Livery"]

data["keys"] = keys_array

with open(jsonPath, 'w', encoding='utf-8') as jsonf:
    jsonf.write(json.dumps(data, indent=4))
