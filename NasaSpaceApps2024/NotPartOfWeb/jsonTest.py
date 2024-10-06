import json
with open("data/NasaNEOData.json", "r") as f:
    data = json.load(f)
print(data.items())