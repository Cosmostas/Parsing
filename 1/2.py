import requests
from pprint import pprint
import json


main_link = 'https://api.vk.com/method'

method = 'groups.get'

header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
          'Accept':'*/*'}

token = '7799bd9af67f9645d1083979a801ee2454241136debe2d45b499fe2bac04000cb729b9212417dda3da61e'
v = '5.110'
params = {
    'access_token' : token,
    'v' : v,
    'extended' : '1'}

link = f'{main_link}/{method}'

response = requests.get(link, headers = header, params=params)

data = response.json()

json.dump(data,open('vksubs.json','w+'))

for i in data['response']['items']:
    pprint(i['name'])
