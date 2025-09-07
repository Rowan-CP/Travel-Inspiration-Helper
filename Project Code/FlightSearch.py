from datetime import datetime
from ApiCalls import API_CALLER
from FormattingData import format_flight_offers_data

#how many flights to display to the user at a time
PER_PAGE = 8

#---Helper functions for specific_flights---

#get a valid integer (can select whether 0 is considered valid)
def get_integer_input(prompt, incl_0):
    while True:
        try:
            num_x = int(input(prompt))

            #Printing an error if the user enters an invalid integer (0 may or may not count)
            if incl_0:
                if num_x < 0:
                    print("Please enter a number >= 0\n")
                    continue
            else:
                if num_x <= 0:
                    print("Please enter a number > 0\n")
                    continue
           
            return num_x

        except ValueError:
            print("Must enter a number (Ex: 2)\n")

#getting a date and ensuring it was entered using the proper format (i.e. YYYY-MM-DD)
def get_date(prompt):
    input_date = input(prompt).strip()
    while True:
        try:
            date_object = datetime.strptime(input_date, "%Y-%m-%d")

            todays_date = datetime.today()

            if date_object > todays_date:
                return date_object
            else:
                input_date = input("Please enter a date later than today's date: ").strip()

        #if the date that was entered cannot be parsed into the proper format (YYYY-MM-DD)
        except ValueError:
            input_date = input("Date must be entered in the following format -> YYYY-MM-DD: ").strip()

#getting and storing information for all the passengers
def get_passenger_info():
    #to aid with user display
    traveler_types = ["ADULT", "CHILD", "HELD_INFANT", "SEATED_INFANT", "SENIOR"]
    traveler_prompts = {
        "ADULT": "adults (age 12–59)",
        "CHILD": "children (age 2–11)",
        "HELD_INFANT": "infants on lap (under 2)",
        "SEATED_INFANT": "infants with seat (under 2)",
        "SENIOR": "seniors (60+)"
    }

    while True:
        #getting num_passengers (incl_0 -> False, must be > 0)
        num_passengers = get_integer_input("Please input the number of passengers: ", False)

        #to add to flight details
        traveler_counts = {
            "ADULT": 0,
            #senior tag must be at this point in the dictionary to facilitate held-infant logic
            #in the format_flight_offers_body() method in the ApiCaller class
            "SENIOR": 0,
            "CHILD": 0,
            "HELD_INFANT": 0,
            "SEATED_INFANT": 0
        }

        remaining = num_passengers
        #asking the number of each type of passenger, stopping when num_passengers has been reached
        for type in traveler_types:
            #if there are still passengers to be accounted for
            if remaining > 0:
                while True:
                    #getting the quantity of the given type of passenger
                    num_type = get_integer_input(f"How many {traveler_prompts[type]}?: ", True)
                    if num_type <= remaining:
                        traveler_counts[type] += num_type
                        remaining -= num_type
                        break
                    else:
                        #making sure user cannot have more of one type of passenger than the total number of passengers they selected
                        print(f"Please enter a number between 0 and {remaining}\n")

        #the user enters 0 passengers
        if remaining == num_passengers:
            print("You cannot enter 0 for all passenger types. Please re-enter your info.\n")

        #there are more held infants than adults
        elif traveler_counts["ADULT"] < traveler_counts["HELD_INFANT"]:
            print("The number of held infants must match the number of adults. Please re-enter your info.\n")

        #there are infants, but no adults or seniors
        elif (traveler_counts["ADULT"] == 0 and traveler_counts["SENIOR"] == 0) and (traveler_counts["SEATED_INFANT"] + traveler_counts["HELD_INFANT"]) > 0:
            print("You must have at least one adult/senior to accompany infants. Please re-enter your info.\n")

        #if the sum of each type of passenger does not equal the total number of passengers they specified,
        #give them the option to keep their new total or re-enter their travel info
        elif remaining > 0:
            print(f"\nHeads up! You said there were {num_passengers} passengers in total but you only accounted for {num_passengers - remaining} of them.")
            next_action = input("Would you like to continue or modify your traveler info? (enter: con/mod): ").strip().lower()

            while next_action not in ('con', 'mod'):
                next_action = input("Please enter 'con' to continue your flight search or 'mod' to modify your traveler info: ").strip().lower()

            if next_action == 'con':
                break
            else:
                #adding a \n for spacing purposes
                print()
        
        else:
            break
    
    return traveler_counts

def get_flight_type():
    trip_prompt = "Type 'rt' if you're looking for a round-trip flight or 'ow' if you're looking for a one-way flight: "
    trip = input(trip_prompt).strip().lower()
    while trip not in ('rt', 'ow'):
        print("--> Must type 'rt' or 'ow' <--\n")
        trip = input(trip_prompt).strip().lower()
        
    print()

    return trip
    

def specific_flights():
    details = dict()

    print("Hey there fellow traveler!👋 Let's find you your perfect flight!✈️\n")

    #---Type of flight (round-trip or one-way)---
    details["trip"] = get_flight_type()

    #---Passengers---
            
    details["travelers"] = get_passenger_info()

    #---Airports---

    print()
    origin_airport = input("Enter origin airport code (Ex: YUL): ").strip().upper()
    destination_airport = input("Enter destination airport code (Ex: LHR): ").strip().upper()

    details["origin_airport"] = origin_airport
    details["destination_airport"] = destination_airport

    #---Dates---

    print()
    dt_departure_date = get_date("Enter your departure date as YYYY-MM-DD (Ex: 2025-06-12): ")
    departure_date = dt_departure_date.strftime("%Y-%m-%d")
    details["departure_date"] = departure_date

    if details.get("trip") == 'rt':
        dt_return_date = get_date("Enter your return date as YYYY-MM-DD (Ex: 2025-06-20): ")
        return_date = dt_return_date.strftime("%Y-%m-%d")
    else:
        return_date = None

    details["return_date"] = return_date

    print("Searching Flights now...\n")
    flight_offers_dict = API_CALLER.get_flight_offers(details)
    if flight_offers_dict:
        format_flight_offers_data(flight_offers_dict, PER_PAGE)

#---Main---
print()

specific_flights()




