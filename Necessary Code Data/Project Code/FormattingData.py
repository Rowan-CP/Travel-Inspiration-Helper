import json
from datetime import datetime
from ApiCalls import API_CALLER
from tabulate import tabulate

AIRLINES_DICT = r"file path of the airlines_dict file"

#type_name refers to "destination_country_name" or "destination_city_name" depending on the grouping criteria
def group_by(type_name, results_list, sorted_list):
    #if results_list is empty, returns an empty list, since function is always called with sorted_list = [] to start
    if not results_list:
        return sorted_list

    first_result = results_list[0]
    #starting a list of all the results with the same name
    group = [first_result]

    #base case
    if len(results_list) == 1:
        sorted_list.extend(group)
        return sorted_list

    name = first_result.get(type_name)

    #looping backwards through list to avoid indexing issues when deleting items from the list
    for i in range(len(results_list) - 1, 0, -1):
        current_result = results_list[i]
        current_name = current_result.get(type_name)

        #if current name matches the first name in the list, 
        #add it to the group and remove it from the original list
        if current_name == name:                  
            group.append(current_result)
            del results_list[i]

    #removing the first result from the original list
    del results_list[0]

    #filtering out duplicate entries - same city name, same airports, same dates
    if type_name == "destination_city_name":
        unique_entries = set()
        unique_group = []

        #getting relevant data from each entry in the group of identical city names
        for entry in group:
            details = (
                entry.get("destination_airport"),
                entry.get("origin_airport"),
                entry.get("departure_date"),
                entry.get("return_date")
            )

            #using set to keep track of entries because O(1) time to check for membership
            #faster than using a list to keep track
            if details not in unique_entries:
                unique_entries.add(details)
                unique_group.append(entry)

        sorted_list.extend(unique_group)

    #type_name == "destination_country_name"
    else:
        sorted_list.extend(group)
    
    #results_list is now shorter
    return group_by(type_name, results_list, sorted_list)

#must pass time_off and duration_range to filter out the responses that don't match
#the user's specifications because the api data sometimes returns results that are
#close enough to the input parameters, but don't strictly respect them
def format_flight_inspo_data(flight_inspo_data_list, time_off, duration_range):
    results_list = []

    for flight_inspo_data in flight_inspo_data_list:
        results = flight_inspo_data.get("data")
        for entry in results:
            entry_dict = dict()

            earliest, latest = time_off
            min_duration, max_duration = duration_range
            
            departure_date = entry.get("departureDate")
            return_date = entry.get("returnDate")
            #dt stands for datetime version, as opposed to str version
            dt_departure_date = datetime.fromisoformat(departure_date)
            dt_return_date = datetime.fromisoformat(return_date)

            trip_length = dt_return_date - dt_departure_date
            #trip_length will be a timedelta object so must extract the number of days
            #+1 because both travel days are included in the trip duration
            trip_length = trip_length.days + 1

            #if the result is not within the allotted window of time off, 
            #or does not meet the duration specifications, then don't include it
            if ((dt_departure_date < earliest or dt_return_date > latest) or
            trip_length < min_duration or trip_length > max_duration):
                continue

            entry_dict["departure_date"] = departure_date
            entry_dict["return_date"] = return_date
            entry_dict["dt_departure_date"] = dt_departure_date
            entry_dict["dt_return_date"] = dt_return_date

            origin_airport_code = entry.get("origin")
            destination_airport_code = entry.get("destination")
            entry_dict["origin_airport"] = origin_airport_code
            entry_dict["destination_airport"] = destination_airport_code

            #getting the city & country name associated with the destination airport
            destination_city_country_dict = API_CALLER.get_location(destination_airport_code)

            entry_dict["destination_city_name"] = destination_city_country_dict.get("city_name")
            entry_dict["destination_country_name"] = destination_city_country_dict.get("country_name")

            #getting the city & country name associated with the origin airport
            origin_city_country_dict = API_CALLER.get_location(origin_airport_code)

            entry_dict["origin_city_name"] = origin_city_country_dict.get("city_name")
            entry_dict["origin_country_name"] = origin_city_country_dict.get("country_name")
    
            results_list.append(entry_dict)

    #sorting the results by country & city
    sorted_by_country_list = group_by("destination_country_name", results_list, [])
    fully_sorted_list = group_by("destination_city_name", sorted_by_country_list, [])

    result_num = 1
    for result in fully_sorted_list:
        print(f"Flight option {result_num}:")
        print(f"\tDestination: {result.get("destination_city_name")}, {result.get("destination_country_name")}")
        print(f"\tAirports: {result.get("origin_airport")} -> {result.get("destination_airport")}")
        #formatting the departure & return dates into a more readable format
        print(f"\t{datetime.strftime(result.get('dt_departure_date'), "%b %d, %Y")} - {datetime.strftime(result.get('dt_return_date'), "%b %d, %Y")}")
        print()

        result_num += 1

    return fully_sorted_list

#---Helper functions for format_flight_offers_data---

#formatting a duration of the form: "PT8H10M"
def format_duration(duration):
    # remove "PT"
    without_PT = duration[2:]

    hours = 0
    mins = 0

    if 'H' in without_PT:
        H_index = without_PT.find('H')
        hours = without_PT[:H_index]
    if 'M' in without_PT:
        M_index = without_PT.find('M')
        # if there was an 'H', take what's after it. Otherwise take from start.
        if 'H' in without_PT:
            mins = without_PT[H_index + 1 : M_index]
        else:
            mins = without_PT[:M_index]

    return f"{hours} hr {mins} min"

def get_leg_info(flight, leg, info_type):
    if leg not in ("outbound", "return") or info_type not in ("airports", "times", "date", "carrier_code"):
        raise ValueError('Usage: get_leg_info(flight, "outbound/return", "airports/times/date/carrier_code")')
    else:
        if leg == "outbound":
            index = 0
        else:
            index = 1
        
        if info_type == "airports":
            air1 = flight.get("itineraries")[index].get("segments")[0].get("departure").get("iataCode")
            air2 = flight.get("itineraries")[index].get("segments")[0].get("arrival").get("iataCode")

            return air1, air2

        if info_type == "carrier_code":
            carrier_code = flight.get("itineraries")[index].get("segments")[0].get("carrierCode")

            return carrier_code

        elif info_type in ("times", "date"):
            #getting departure and arrival times
            departure_info = flight.get("itineraries")[index].get("segments")[0].get("departure").get("at")
            arrival_info = flight.get("itineraries")[index].get("segments")[0].get("arrival").get("at")

            departure_datetime_object = datetime.fromisoformat(departure_info)
            arrival_datetime_object = datetime.fromisoformat(arrival_info)

            if info_type == "times":
                #%I -> Hour | %M -> Minutes | %p -> AM or PM
                #lstrip used to get rid of the leading 0 on the hour
                formatted_departure_time = departure_datetime_object.strftime("%#I:%M %p").lstrip("0")
                formatted_arrival_time = arrival_datetime_object.strftime("%#I:%M %p").lstrip("0")

                return formatted_departure_time, formatted_arrival_time
            else:
                #%b -> abbreviated month (Ex: Jul) | %d -> Day | %Y -> Year (2025)
                formatted_date = departure_datetime_object.strftime("%b %d, %Y")

                return formatted_date

def get_airline(carrier_codes):
    carrier_code_map = dict.fromkeys(carrier_codes)

    #getting the dictionary of known airlines
    with open(AIRLINES_DICT, "r") as file:
        airlines_dict = json.load(file)

    #updating the dictionary of known airlines if certain carrier codes are 
    #not currently mapped to their corresponding airline
    to_lookup = []
    for carrier_code in carrier_codes:
        if carrier_code not in airlines_dict:
            to_lookup.append(carrier_code)

    #if there are carrier codes that have yet to be added to the known airlines dictionary,
    #look up their corresponding airlines and add them to the dictionary
    if len(to_lookup) > 0:
        joined_to_lookup = ", ".join(to_lookup)

        airlines_dict = API_CALLER.get_airline_data(joined_to_lookup, airlines_dict)

        #Write the updated dictionary of known airlines back to the airlines file
        with open(AIRLINES_DICT, "w") as file:
            json.dump(airlines_dict, file, indent = 2)

    #returning a dictionary including only the requested carrier code - airline mappings
    for carrier_code in carrier_codes:
        carrier_code_map[carrier_code] = airlines_dict.get(carrier_code)

    #the dictionary containing only the mappings of the codes that were passed to be looked up
    return carrier_code_map

def get_travelers(flight):
    #getting number of travelers
    travelers_data = flight.get("travelerPricings")
    travelers_dict = {"ADULT": 0, "CHILD": 0, "SENIOR": 0, "SEATED_INFANT": 0, "HELD_INFANT": 0}

    for traveler in travelers_data:
        traveler_type = traveler.get("travelerType")
        if traveler_type in ("ADULT", "CHILD", "SENIOR", "SEATED_INFANT", "HELD_INFANT"):
            travelers_dict[traveler_type] += 1

    label_map = {
        "ADULT": "Adult",
        "CHILD": "Child",
        "SENIOR": "Senior",
        "SEATED_INFANT": "Seated Infant",
        "HELD_INFANT": "Held Infant"
    } 

    #building the output string
    travelers = []
    for traveler_type, count in travelers_dict.items():
        if count > 0:
            label = label_map.get(traveler_type)
            #Add 's' for pluralization if needed
            if count > 1:
                label += "s"
            travelers.append(f"{count} {label}")

    formatted_travelers = "\n".join(travelers)
    return formatted_travelers


def format_flight_offers_data(flight_offers_dict, per_page):
    flight_count = 0

    #no flights were found
    data = flight_offers_dict.get("data")
    if not data:
        print("Sorry, no specific flights match your search criteria. Maybe alter your budget and try again!")
        return None

    print("\nFlights: \n")

    for flight in data:
        if (flight_count != 0) and (flight_count % per_page == 0):
            answer = "null"
            while answer not in ("y", "n"):
                answer = input("Would you like to see more offers (y/n)?: ").strip().lower()

            if answer == "n":
                break

        #---Outbound Flight Info---

        #getting duration of departing flight
        outbound_duration = flight.get("itineraries")[0].get("duration")
        formatted_outbound_duration = format_duration(outbound_duration)

        #getting outbound airports
        outbound_air1, outbound_air2 = get_leg_info(flight, "outbound", "airports")

        #getting departure date
        departure_date = get_leg_info(flight, "outbound", "date")

        #getting departure and arrival times for outbound flight
        outbound_departure_time, outbound_arrival_time = get_leg_info(flight, "outbound", "times")

        #getting carrier code for outbound flight
        outbound_carrier_code = get_leg_info(flight, "outbound", "carrier_code")

        #formatted string with outbound flight info
        outbound_info = f"""{departure_date}
{outbound_air1} -> {outbound_air2}
{formatted_outbound_duration}
{outbound_departure_time} - {outbound_arrival_time}"""

        #---General Trip Info---

        #getting total price for all travelers for all legs of the trip
        currency = flight.get("price").get("currency")
        total_price = flight.get("price").get("grandTotal")
        formatted_price = f"${total_price} {currency}"

        #getting all travelers info
        formatted_travelers = get_travelers(flight)

        if len(flight.get("itineraries")) == 2:
            round_trip = "Yes"

            #---Return Flight Info---

            #getting duration of return flight
            return_duration = flight.get("itineraries")[1].get("duration")
            formatted_return_duration = format_duration(return_duration)

            #getting return airports
            return_air1, return_air2 = get_leg_info(flight, "return", "airports")

            #getting return date
            return_date = get_leg_info(flight, "return", "date")

            #getting departure and arrival times for return flight
            return_departure_time, return_arrival_time = get_leg_info(flight, "return", "times")

            #getting carrier code for return flight
            return_carrier_code = get_leg_info(flight, "return", "carrier_code")

            #getting names of departure and return airlines
            carrier_code_dict = get_airline([outbound_carrier_code, return_carrier_code])
            outbound_airline = carrier_code_dict.get(outbound_carrier_code)
            return_airline = carrier_code_dict.get(return_carrier_code)
        
            if outbound_airline == return_airline:
                formatted_airlines = f"✈  {outbound_airline}"
            else:
                formatted_airlines = f"✈ ->: {outbound_airline}\n<-✈ : {return_airline}"

            #formatted string with return flight info 
            return_info = f"""{return_date}
{return_air1} -> {return_air2}
{formatted_return_duration}
{return_departure_time} - {return_arrival_time}"""

            #---Printing Table---

            #return_info, carryOn_included, formatted_airline
            flight_info = [round_trip, formatted_travelers, formatted_price, outbound_info, return_info, formatted_airlines]
            #"Return", "Carry-On Included", "Airline(s)"
            table_headers = ["Round-trip", "Passengers", "Total Price", "Outbound", "Return", "Airline(s)"]
            print(tabulate([flight_info], headers = table_headers, tablefmt = "fancy_grid"))
            print("\n")

        
        elif len(flight.get("itineraries")) == 1:
            round_trip = "No"

            #getting airline name for outbound flight only
            outbound_airline = get_airline([outbound_carrier_code]).get(outbound_carrier_code)
            formatted_airline = f"✈  {outbound_airline}"

            flight_info = [round_trip, formatted_travelers, formatted_price, outbound_info, formatted_airline]
            table_headers = ["Round-trip", "Passengers", "Total Price", "Leg Info", "Airline"]
            print(tabulate([flight_info], headers = table_headers, tablefmt = "fancy_grid"))
            print("\n")
    
        #another flight has just been displayed
        flight_count += 1
