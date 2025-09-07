# Travel Inspiration Helper
✈️Find your next dream destination—and the flight to take you there!

This project comes with two main programs:

Flight Inspiration – A tool for when you've got the travel bug and some vacation time, but you’re not sure where to go. It takes some basic input from the user, suggests a list of possible destinations, lets you pick one, and then pulls up flights to that location.

Flight Search – A more focused search tool. Here, you provide specific details (like origin & destination airports, dates, and passenger info), and it returns all the flights that match your criteria — kind of like a simplified version of Google Flights!

# Important Note:

This project functions by getting flight data, through API calls, from a website called Amadeus for Developers. To do so, it uses API keys that must be kept private. To run this project locally, you would need to replace the API keys at the top of the file called ApiCalls with your own working keys. 

However, there are also two walkthrough files that showcase sample runs of each main program. These let you see how the programs look and behave in action. No need to set up your own API keys first!

# What I learned / Skills I demonstrated in this project

## API usage: 
Taught myself how to use and format API calls to get relevant data from sites like Amadeus for Developers.

## OOP:
Implemented a class in ApiCalls.py that encapsulates all flight API interactions — formatting & making requests, error handling, token fetching & refreshing, and response parsing — improving reusability and maintainability.

## Modular programming:
Organized the project into four modules with clear separation of concerns: two main programs for user interface, one for API integration and parsing, and one for formatting data into user-friendly output.

## Working with external libraries (json, requests, time, datetime, tabulate):
&nbsp;&nbsp;&nbsp;&nbsp;**json** – Learned how to structure API request bodies and how to load/dump JSON data to and from external files for storage and retrieval (Ex: &nbsp;&nbsp;&nbsp;&nbsp;accessing & updating the airport locations file).

&nbsp;&nbsp;&nbsp;&nbsp;**requests** – Gained experience making HTTP requests to external APIs, handling parameters, headers, and parsing responses.

&nbsp;&nbsp;&nbsp;&nbsp;**time** – Used for detecting when an API token has expired and needs to be refreshed.

&nbsp;&nbsp;&nbsp;&nbsp;**datetime** – Worked with dates and times for input validation, formatting, and calculating ranges (e.g. trip durations).

&nbsp;&nbsp;&nbsp;&nbsp;**tabulate** – Learned to present data in clean, readable tables for a better user experience.

## Input validation:
Used try/except blocks to catch invalid input and prompt the user to re-enter correct information before continuing.
Ex: In get_date() and get_duration() functions in FlightInspiration.py.

**Some functionalities related to input handling include...**\
**(User will be re-prompted if they enter invalid answers in any one of these scenarios)**

&nbsp;&nbsp;&nbsp;&nbsp;-User must enter valid numbers (non-negative, greater than 0, not strings), where prompted.

&nbsp;&nbsp;&nbsp;&nbsp;-User must enter dates in the following format, YYYY-MM-DD.

&nbsp;&nbsp;&nbsp;&nbsp;-User must enter a date that is later than the present date.
  
**In FlightInspiration program only:**

&nbsp;&nbsp;&nbsp;&nbsp;-When entering a range of dates that specify a window of time-off, the range must be in ascending order.

&nbsp;&nbsp;&nbsp;&nbsp;-The duration of a trip cannot exceed the length of the specified window of time-off.

&nbsp;&nbsp;&nbsp;&nbsp;-Must enter at least one city of origin to fly from. Cannot immediately type done when entering   origin cities.

&nbsp;&nbsp;&nbsp;&nbsp;-Notifies the user if they try and enter the same origin city twice and does not let them.

&nbsp;&nbsp;&nbsp;&nbsp;-When choosing a flight option number from the list of possible flight destinations, user cannot select a number that is not among the list.

**In FlightSearch program only:**

&nbsp;&nbsp;&nbsp;&nbsp;-When inputting traveler info, user cannot have more of one type of passenger than the total number of passengers they selected. Ex: 3 &nbsp;&nbsp;&nbsp;&nbsp;passengers total, user selects 4 adults.

&nbsp;&nbsp;&nbsp;&nbsp;-Cannot enter 0 for all passenger types.

&nbsp;&nbsp;&nbsp;&nbsp;-If the sum of each type of passenger is less than the total number of passengers selected by the  user, they will be notified by the program &nbsp;&nbsp;&nbsp;&nbsp;and given the option to modify their traveler info or continue with the data that they already entered. Must enter either 'con' or 'mod' at &nbsp;&nbsp;&nbsp;&nbsp;this stage.

&nbsp;&nbsp;&nbsp;&nbsp;-Infants must be accompanied by at least one adult or senior.

&nbsp;&nbsp;&nbsp;&nbsp;-The number of held infants must equal the number of adults/seniors.

## Algorithms:
**Levenshtein Distance Algorithm:** \
Functionality: Handles user typos in city names. If a city is slightly misspelled when entered as an origin, the program suggests possible correct spellings based on a large dataset mapping city names to their codes.

Implementation: I learned about and then implemented my own version of the Levenshtein distance algorithm (in the min_distance() function of FlightInspiration.py) to measure how similar two words are. In the did_you_mean() function, I convert this distance into a similarity score by comparing it against the maximum number of possible operations it takes to go from one word to the other (the length of the longer word). If the score meets or exceeds a threshold ratio (chosen through trial and error), the word is added to the list of suggested alternatives.

**Recursive Sorting Algorithm:**\
Functionality: Groups and sorts a list of flight options by either country or city, so that all flights with the same destination are organized together in the final sorted list.

Implementation: The algorithm works recursively. It starts by selecting the first entry in the list, extracting its destination (country or city), and placing it into a new group (a list). It then scans through the remaining entries, starting from the end of the list (to avoid indexing issues when removing items), adding any flights with the same destination into the group. When a match is added to the group, it is deleted from the original list. Once all matches are found, the group is added to the sorted list, and the function calls itself again with the shorter list of remaining entries.

For sorting based on city, the algorithm also removes duplicates by checking each entry’s destination airport, origin airport, and travel dates. This ensures that the final output contains only unique flights, even if multiple identical results appear in the raw data.

The process continues until the input list is empty, at which point the sorted list is complete.
