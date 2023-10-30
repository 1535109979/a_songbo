import requests

# res = requests.post('http://127.0.0.1:8080/')
res = requests.get('http://127.0.0.1:8080/')
print(res.text)
