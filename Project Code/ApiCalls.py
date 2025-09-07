import json
import time
import requests

TEST_API_KEY = "test_api_key"
TEST_API_SECRET = "test_api_secret"

PROD_API_KEY = "prod_api_key"
PROD_API_SECRET = "prod_api_secret"

ENV = "production"

AIRPORT_LOCATIONS_FILE = r"file path of the airport_locations file"
CITY_CODES_FILE = r"file path of the city_codes file"

class ApiCaller:
    def __init__(self):
        if ENV == "test":
            self.api_key = TEST_API_KEY
            self.api_secret = TEST_API_SECRET
            self.base_url = "https://test.api.amadeus.com"
        elif ENV == "production":
            self.api_key = PROD_API_KEY
            self.api_secret = PROD_API_SECRET
            self.base_url = "https://api.amadeus.com"

        self.token = ""
        self.token_expires_at = 0
        #fetching a token to start
        self.__token_refresh()

    def __token_refresh(self):
        token_endpoint = "/v1/security/oauth2/token"
        url = self.base_url + token_endpoint

        token_headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        token_data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }

        response = requests.post(url, headers = token_headers, data = token_data)
        response_dict = response.json()
        
        self.token = response_dict.get("access_token")

        #I am saying that it expires 2 mins earlier than it actually does to provide a buffer
        expires_in = response_dict.get("expires_in") - 120
        #time.time() gives current time in seconds
        self.token_expires_at = time.time() + expires_in

    def __token_check(self):
        if time.time() > self.token_expires_at:
            self.__token_refresh()

    def __get_headers(self):
        self.__token_check()
        return {
            "Authorization": "Bearer " + self.token
        }

    #displays the error message upon a failed api call
    def __display_error(self, response):
        print("API call failed with status_code: ", response.status_code)
        print("Error message: ", response.text)

    def __call_location_api(self, sub_type, keyword):
        location_endpoint = f"/v1/reference-data/locations"

        url = self.base_url + location_endpoint
        headers = self.__get_headers()

        #sub_type is city or airport, keyword is a spelling of a city name or an airport code
        params = {
            "subType": sub_type,
            "keyword": keyword
        }

        response = requests.get(url, headers = headers, params = params)

        if response.status_code == 200:
            return response.json()
            
        else:
            self.__display_error(response)
            return None

    #get the name of the city & country that an airport is located in
    def get_location(self, airport_code):
        with open(AIRPORT_LOCATIONS_FILE, "r") as file:
            airport_locations_dict = json.load(file)

        city_country_dict = airport_locations_dict.get(airport_code)
        
        #if the given airport code is not already within the dictionary,
        #search it up using the location api
        if not city_country_dict:
            response_dict = self.__call_location_api("AIRPORT", airport_code)

            #call failed or call succeeded but the api could not find the associated country
            #and city name for the given airport code i.e. data is []
            if not response_dict or not response_dict.get("data"):
                return {"city_name": "Unknown", "country_name": "Unknown"}

            #call succeeded and returned valid data
            city_name = response_dict.get("data")[0].get("address").get("cityName").lower()
            country_name = response_dict.get("data")[0].get("address").get("countryName").lower()

            #formatting location names
            city_name = city_name.capitalize()
            country_name = country_name.capitalize()

            #create the entry for airport_code from the data returned by the api search
            city_country_dict = {
                "city_name": city_name,
                "country_name": country_name
            }

            #update the dictionary
            airport_locations_dict[airport_code] = city_country_dict
            with open(AIRPORT_LOCATIONS_FILE, "w") as file:
                json.dump(airport_locations_dict, file, indent = 2)

        return city_country_dict

    def get_city_code(self, city_name):
        response_dict = self.__call_location_api("CITY", city_name)

        #call failed or call succeeded and no city names matched the search string
        if not response_dict or not response_dict.get("data"):
            print(f"Sorry, no matches found for {city_name}")
            return None

        data = response_dict.get("data")

        city_code = data[0].get("address").get("cityCode")
        city_name = data[0].get("address").get("cityName").lower()

        #accessing the dictionary mapping city names to their codes
        with open(CITY_CODES_FILE, "r") as file:
            city_code_dict = json.load(file)

        #updating the dictionary and writing it back to the file
        city_code_dict[city_name] = city_code

        with open(CITY_CODES_FILE, "w") as file:
            json.dump(city_code_dict, file, indent = 2)

        return city_code
    
    def get_airline_data(self, joined_to_lookup, airlines_dict):
        airline_data_endpoint = f"/v1/reference-data/airlines?airlineCodes={joined_to_lookup}"

        url = self.base_url + airline_data_endpoint   
        headers = self.__get_headers()

        response = requests.get(url, headers = headers)

        #if api call successful
        if response.status_code == 200:
            response_dict = response.json()

            for airline in response_dict.get("data", []):
                airlines_dict[airline.get("iataCode")] = airline.get("businessName")

        else:
            self.__display_error(response)

        return airlines_dict

    def format_flight_offers_body(self, input_dict):
        #formatting the list of travelers
        travelers_list = []
        cur_id = 1
        held_infant_counter = 1
        traveler_counts = input_dict.get("travelers")

        #order will be: adults, seniors, children, held-infants, seated-infants
        for traveler_type in traveler_counts:
            traveler_type_quantity = traveler_counts.get(traveler_type)
            #if there is more than 0 travelers of the given type
            if traveler_type_quantity > 0:
                #add each traveler of that type with a unique id
                for x in range(traveler_type_quantity):
                    #include an associated adult for held infants. Since adults and seniors are given id's first,
                    #and the logic in main.py ensures held infants won't exceed the number of adults + seniors,
                    #this logic will work                   
                    if traveler_type == "HELD_INFANT":
                        travelers_list.append({"id": str(cur_id), "travelerType": traveler_type, "associatedAdultId": str(held_infant_counter)})
                        held_infant_counter += 1
                    else:
                        travelers_list.append({"id": str(cur_id), "travelerType": traveler_type})

                    cur_id += 1

        #getting airports
        origin_airport = input_dict.get("origin_airport")
        destination_airport = input_dict.get("destination_airport")

        #dates
        departure_date = input_dict.get("departure_date")
        return_date = input_dict.get("return_date")

        trips_list = [{
            "id": "1",
            "originLocationCode": origin_airport,
            "destinationLocationCode": destination_airport,
            "departureDateTimeRange": {
                "date": departure_date
            }
        }]

        trip_ids = ["1"]

        #adding the return leg if the user selected round-trip flights
        if input_dict.get("trip") == 'rt':
            trips_list.append({
                "id": "2",
                "originLocationCode": destination_airport,
                "destinationLocationCode": origin_airport,
                "departureDateTimeRange": {
                    "date": return_date
                }
            })

            trip_ids.append("2")

        body = {
            "currencyCode": "CAD",
            "originDestinations": trips_list,
            "travelers": travelers_list,
            "sources": ["GDS"],
            "searchCriteria": {
                "maxFlightOffers": 50,
                "maxPrice": input_dict.get("max_price"),
                "flightFilters": {
                    "connectionRestriction": {
                        "maxNumberOfConnections": 0
                    },
                    "cabinRestrictions": [
                        {
                            "cabin": "ECONOMY",
                            "coverage": "ALL_SEGMENTS",
                            "originDestinationIds": trip_ids
                        }
                    ]
                }
            }
        }

        return body

    def format_cheapest_cities_body(self, input_dict):
        body = {
            "origin": input_dict.get("origin_city_code"),
            "departureDate": input_dict.get("departure_date_range"),
            "oneWay": "false",
            "duration": input_dict.get("duration")
        }

        return body

    def get_flight_offers(self, input_dict):
        flight_offers_endpoint = "/v2/shopping/flight-offers"

        url = self.base_url + flight_offers_endpoint
        headers = self.__get_headers()

        #getting the body of the request, based on user input     
        request_body = self.format_flight_offers_body(input_dict)

        #making the api call
        response = requests.post(url, headers = headers, json = request_body)

        #if api call successful
        if response.status_code == 200:
            response_dict = response.json()

            return response_dict

        #call failed
        else:
            self.__display_error(response)
            return None

    def get_cheapest_cities(self, input_dict, origin_city_codes):
        cheapest_cities_endpoint = "/v1/shopping/flight-destinations"

        url = self.base_url + cheapest_cities_endpoint
        headers = self.__get_headers()

        response_dict_list = []
        for city_code in origin_city_codes:
            #note that this changes input_dict in each iteration. This is fine since input_dict
            #will not be used after the execution of this function
            input_dict["origin_city_code"] = city_code

            #getting the body of the request, based on user input
            request_body = self.format_cheapest_cities_body(input_dict)

            response = requests.get(url, headers = headers, params = request_body)

            #if api call successful
            if response.status_code == 200:
                response_dict = response.json()

                response_dict_list.append(response_dict)

            else:
                self.__display_error(response)
                response_dict_list = []

        return response_dict_list

#defining this here to be used across all other files
API_CALLER = ApiCaller()
