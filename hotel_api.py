import googlemaps
import pprint


def hotel(lat, lng):
    API_key = 'AIzaSyBRIO82noSEHGTvOwFZICuRwmBoQ-BoU0Y'
    gmaps = googlemaps.Client(key=API_key)

    places_info = gmaps.places_nearby(location=str(lat) + ',' + str(lng), radius=2500, type='lodging')

    hotel_options = []
    for place in places_info['results']:
        myplace = place['place_id']

        myfields = ['name', 'formatted_phone_number', 'formatted_address', 'icon', 'rating']

        place_details = gmaps.place(place_id=myplace, fields=myfields)
        hotel_options.append(place_details['result'])
    filtered_options = []
    for i in hotel_options:
        if 'rating' in i.keys():
            filtered_options.append(i)
    sorted_hotels = sorted(filtered_options, key=lambda i: i['rating'])
    filtered_hotels = list({d['name']: d for d in sorted_hotels}.values())[:6]
    return filtered_hotels
