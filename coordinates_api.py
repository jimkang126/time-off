import json
import requests


def coordinates(destination):
    url = "https://airport-info.p.rapidapi.com/airport"

    querystring = {"iata": destination}
    headers = {
        'x-rapidapi-host': "airport-info.p.rapidapi.com",
        'x-rapidapi-key': "61897ca58emsh5018369ec59f29ep190a4fjsnccb224937c08"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response_json = json.loads(response.text)

    latitude = response_json["latitude"]
    longitude = response_json["longitude"]
    final_query = {'latitude': latitude, 'longitude': longitude}

    return final_query
