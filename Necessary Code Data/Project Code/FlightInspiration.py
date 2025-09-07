import json
from datetime import datetime, timedelta
from ApiCalls import API_CALLER
from FormattingData import format_flight_inspo_data, format_flight_offers_data

#max number of cities the user can select to fly from
MAX_CITIES = 5
SIMILARITY_RATIO = 0.65
#how many flights to display to the user at a time
PER_PAGE = 8

CITY_CODES_FILE = r"file path of the city_codes file"

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

def get_duration():
    while True:
        dur_input = input("\nEnter the duration of your trip in days (Ex: 8) (Can be a range: Ex: 8,10): ").strip().split(",")

        try:
            if len(dur_input) == 1:
                #ensuring user entered a valid integer value
                num = int(dur_input[0])
                duration = str(num)

                min_duration = max_duration = num

                #the flight inspiration search api cannot accept trips longer than 15 days
                if num == 0 or num > 15:
                    print("Trip must be between 1 and 15 days.")
                    continue

            elif len(dur_input) == 2:
                #ensuring user entered valid integer values
                num1 = int(dur_input[0])
                num2 = int(dur_input[1])

                if num1 == 0 or num2 == 0 or num1 > 15 or num2 > 15:
                    print("Trip must be between 1 and 15 days...")
                    continue

                min_duration = min(num1, num2)
                max_duration = max(num1, num2)

                #the user entered a range of the same number, i.e. 8,8
                if min_duration == max_duration:
                    duration = str(min_duration)
                else:
                    duration = f"{min_duration},{max_duration}"

            #duration is the formatted string to send to the api, min_duration & max_duration
            #are integers representing the bounds of the duration range for date comparison purposes
            return duration, min_duration, max_duration

        except ValueError:
            print("Please enter valid number(s).")

#calculating how many operations it takes to transform one string into another
#using the levenshtein distance algorithm
def min_distance(word1, word2):
    matrix = []
    #initializing a 2D matrix with number of rows correponding to number of letters in word1 + 1,
    #and number of columns corresponding to number of letter in word2 + 1
    for i in range(len(word1) + 1):
        #float("inf") gives positive infinity. Acts as a placeholder since inf is not a valid entry
        #in the computations
        row = [float("inf")] * (len(word2) + 1)
        matrix.append(row)

    #initializing the first row and first column
    for j in range(len(word2) + 1):
        matrix[0][j] = j
    for i in range(len(word1) + 1):
        matrix[i][0] = i
    
    #performing the algorithm
    for i in range(1, len(word1) + 1):
        for j in range(1, len(word2) + 1):
            #i - 1 and j - 1, since my ranges start at 1 but I want to start at the first letter of each word
            if word1[i - 1] == word2[j - 1]:
                matrix[i][j] = matrix[i - 1][j - 1]
            else:
                minimum = min(matrix[i - 1][j - 1], matrix[i - 1][j], matrix[i][j - 1])
                matrix[i][j] = minimum + 1

    return matrix[len(word1)][len(word2)]

#suggests alternate spellings for a city name, based on the entries in the city_dict
def did_you_mean(input_city, city_dict):
    suggestions = []
    for city in city_dict:
        #1 - (num_edits / num_possible_edits)
        similarity = 1 - (min_distance(input_city, city) / max(len(input_city), len(city)))

        if similarity >= SIMILARITY_RATIO:
            suggestions.append(city)

    return suggestions

def lookup_city(city_name):
    verify = input(f"Please verify {city_name} is spelled correctly and type 'yes' if so. \nOtherwise, please re-enter your city: ").strip().lower()
    
    if verify != 'yes':
        city_name = verify

    #look up the city name using the airport & city search api
    print("Searching city name...")
    city_code = API_CALLER.get_city_code(city_name)

    return city_code

#returns a list of city codes to search based on user input of city names. Takes city_dict as input
#to search up the user inputted names in the dictionary that maps city names to their codes
def get_city_codes_to_search(city_dict):
    print("\nWhat city/cities are you interested in flying out of (Type 'done' once finished entering city names)?: ")
    
    #the list of codes to search up using flight inspiration api
    city_code_list = []
    num_cities = 0

    while num_cities < MAX_CITIES:
        city_name = input("Enter city name (Ex: London): ").strip().lower()
        
        #guarding against the user simply pressing enter
        if not city_name:
            print("Must enter a city name or type 'done'.")
            continue

        #exit the loop if user enters done, provided they already entered at least one city name
        if city_name == "done":
            if num_cities == 0:
                print("Must enter at least one city name...")
                continue
            else:
                #blank line for formatting purposes
                print()
                break

        #getting city code of user input
        city_code = city_dict.get(city_name)

        #city_code in dictionary
        if city_code:
            #ensuring user doesn't enter same city twice
            if city_code in city_code_list:
                print("You already entered that one!")
                continue

            #add city_code to list of codes
            city_code_list.append(city_code)
            num_cities += 1

        #city_code not in dictionary
        else:
            #display alternate spellings
            suggestions = did_you_mean(city_name, city_dict)
            #suggestions exist
            if len(suggestions) > 0:
                print("Did you mean one of the following...")
                for city in suggestions:
                    print(city)

                #check if desired city among suggestions. Ensure user doesn't enter a new city name not among suggestions
                while True:
                    answer = input("Enter 'no' or the name of the city you meant with the exact spelling as above: ").strip().lower()
                
                    if answer == "no":
                        #look up the city name they entered
                        city_code = lookup_city(city_name)

                        #city searched was a valid city
                        if city_code:
                            city_code_list.append(city_code) 
                            num_cities += 1  

                        break                 
                    
                    elif answer in suggestions:
                        city_code = city_dict.get(answer)

                        #ensuring user doesn't enter same city twice
                        if city_code in city_code_list:
                            print("You already entered that one!")
                        
                        else:
                            #add the city code to the list of codes to search up
                            city_code_list.append(city_code)
                            num_cities += 1

                        break

            #no suggestions exist
            else:
                #look up the city name they entered
                city_code = lookup_city(city_name)

                #city searched was a valid city
                if city_code:
                    city_code_list.append(city_code)
                    num_cities += 1

    if num_cities == MAX_CITIES:
        print(f"Sorry, you can only enter up to {MAX_CITIES} cities... I like your flexibility though!\n")
        
    return city_code_list

def user_interface():
    print("""\nHey fellow traveler👋 Dreaming of a getaway, but not sure where to go? 
No worries - your travel inspo helper is here!
Just tell us a few basics like your budget, your time off, and we'll show you a list 
of possible destinations you can get to with ease. If one of em strikes your fancy, 
feel free to follow up with our specific flight search for more details.
Now let's get you outta here!✈️\n""")


    details = dict()

    #---Getting budget
    budget = input("First up, what's your budget?: $")
    while True:
        try:
            #ensuring user entered a valid float value, then rounding it to an int
            budget = round(float(budget))

            if budget <= 0:
                budget = input("Please enter a number greater than 0 (Ex: 600): ")
                continue
            break
        except ValueError:
            #protect against user entering a string
            budget = input("Please enter a number (Ex: 1200): ")

    #---Getting time-off window---
    print("\nEnter the window of time you have off (Ex: from: 2025-08-12 to: 2025-08-14)")
    while True:
        earliest = get_date("from: ")
        latest = get_date("to: ")
        time_off = (earliest, latest)

        if earliest <= latest:
            break
        else:
            print("Range must be in ascending order...")


    #---Getting duration & departure date range---
    while True:
        duration, min_duration, max_duration = get_duration()
        details["duration"] = duration
        duration_range = (min_duration, max_duration)

        #This formula is to reduce the number of results where the return dates will exceed
        #the window of time off, but won't exclude any trip possibilities
        #latest possible return date - minimum duration of trip + 1 because both travel days included
        latest_departure_date = latest - timedelta(days = (min_duration - 1))
        if latest_departure_date < earliest:
            print("The duration of your trip cannot be longer than your window of time off.")
        else:
            break

    #putting the departure dates in a format the api will understand
    departure_date_range = ",".join([earliest.strftime("%Y-%m-%d"), latest_departure_date.strftime("%Y-%m-%d")])
    details["departure_date_range"] = departure_date_range

    #---Getting departure city(ies)---
    #getting dictionary mapping city names to city codes
    with open(CITY_CODES_FILE, "r") as file:
        city_dict = json.load(file)

    origin_city_codes = get_city_codes_to_search(city_dict)

    print("Finding your dream destination...\n")
    flight_inspo_data_list = API_CALLER.get_cheapest_cities(details, origin_city_codes)
    fully_sorted_list = format_flight_inspo_data(flight_inspo_data_list, time_off, duration_range)

    #only prompt user for next search if flight options were available
    if len(fully_sorted_list) > 0:
        while True:
            flight_num = input("Want more info about one of the options listed above and interested in similar alternatives?\nEnter the flight option number (Ex: 2). Otherwise, type 'done': ").strip()
            print()

            if flight_num.lower() == "done":
                break
            
            if flight_num.isdigit():
                flight_num = int(flight_num)
                
                if flight_num == 0 or flight_num > len(fully_sorted_list):
                    print("--> Number must correspond to one of the flight option numbers.\n")
                    continue
                
                #since the flight option numbers start at 1
                selected_flight_entry = fully_sorted_list[flight_num - 1]

                selected_flight_entry["max_price"] = budget
                #hard-coding these fields since just wanting to perform a general flight search
                selected_flight_entry["trip"] = "rt"
                selected_flight_entry["travelers"] = {"ADULT": 1}

                #call the flight offers search api
                flight_offers_dict = API_CALLER.get_flight_offers(selected_flight_entry)
                #if the call succeeded
                if flight_offers_dict:
                    format_flight_offers_data(flight_offers_dict, PER_PAGE)
                break
            else:
                print("Please enter a valid number or type 'done'.\n")

    else:
        print("Shoot! It looks like no flight destinations matched your search...\nBetter luck next time!")


#---Main---
user_interface()
