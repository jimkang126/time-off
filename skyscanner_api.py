import json
import requests
import pprint
import time


def get_key(originPlace, destinationPlace, departureDate, returnDate):
    url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/v1.0"

    payload = "inboundDate=" + returnDate + "&cabinClass=economy&children=0&infants=0&country=US&currency=USD&locale=en-US&originPlace=" + originPlace + "-sky&destinationPlace=" + destinationPlace + "-sky&outboundDate=" + departureDate + "&adults=1"
    headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': "c0ab256899msh82354dd27f8d840p167233jsn245555ab9cc7",
        'content-type': "application/x-www-form-urlencoded"
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    time.sleep(7)
    session_key = response.headers['Location'].split("/")[-1]
    return session_key


def flight_info(session_key):
    url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/uk2/v1.0/" + session_key

    querystring = {"sortType": "price", "sortOrder": "asc", "pageIndex": "0", "pageSize": "10"}

    headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': "c0ab256899msh82354dd27f8d840p167233jsn245555ab9cc7"
        }

    returns = requests.request("GET", url, headers=headers, params=querystring)
    time.sleep(5)
    data = json.loads(returns.text)

    agents_response = data['Agents']
    itineraries_response = data['Itineraries']

    agent_data = {}
    for agent in agents_response:
        agent_id = agent["Id"]
        agent_data[agent_id] = {"Name": agent['Name'], "ImageUrl": agent['ImageUrl']}

    itinerary_data = []
    for itinerary in itineraries_response:
        for price_option in itinerary['PricingOptions']:
            agent_id = price_option['Agents'][0]
            deep_link_url = price_option['DeeplinkUrl']
            price = price_option['Price']
            itinerary_data.append({'AgentId': agent_id, 'DeeplinkUrl': deep_link_url, 'Price': price})

    sorted_itinerary_data = sorted(itinerary_data, key=lambda i: i['Price'])
    filtered_itinerary_data = list({d['AgentId']: d for d in sorted_itinerary_data}.values())[:10]

    flight_options = []
    for itinerary in filtered_itinerary_data:
        agent_id = itinerary['AgentId']
        itinerary['Agent'] = agent_data[agent_id]
        flight_options.append({
            'Name': itinerary['Agent']['Name'],
            'ImageUrl': itinerary['Agent']['ImageUrl'],
            'Price': itinerary['Price'],
            'DeeplinkUrl': itinerary['DeeplinkUrl']
        })

    return flight_options
