import requests
from pprint import pprint

url = "https://api.intelligence.io.solutions/api/v1/models"

headers = {
    "accept":"application/json",
    "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjA4NmRhZTRlLWRmOTMtNDE2ZC1hZTM1LTNjZDk1Nzk3MGMxZCIsImV4cCI6NDkwNjc3Nzk0NH0.UIB9XtvXh5LHcuExXksgvK6ySnkZen2sECRElfmWyiH2lUXcaQS0RJhAf8tr68h4h9-tGsM4Sye99z0prclPNg",#ВАШ API-ТОКЕН
}

response = requests.get(url, headers = headers)
pprint(response.json())

for i in range(len(response.json()['data'])):
    print(response.json()['data'][i]['id'])