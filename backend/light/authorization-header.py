import requests

token = "{token}"

headers = {
    "Authorization": "Bearer %s" % token,
}

response = requests.get('https://api.lifx.com/v1/lights/all', headers=headers)
