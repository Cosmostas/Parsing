import requests
from pprint import pprint
import json

main_link = 'https://api.github.com'
username = 'Cosmostas'
link = (f'{main_link}/users/{username}/repos')


response = requests.get(link)

data = response.json()

json.dump(data,open('repos.json','w+'))

for i in data:
    pprint(i['name'])


