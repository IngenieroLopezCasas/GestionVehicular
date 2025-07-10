import requests

res = requests.get("http://localhost:5000/vehicles")
print(res.status_code)
print(res.json())

