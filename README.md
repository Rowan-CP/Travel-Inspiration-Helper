# Travel Inspiration Helper
✈️Find your next dream destination—and the flight to take you there!

This project comes with two main programs:

Flight Inspiration – A tool for when you've got the travel bug and some vacation time, but you’re not sure where to go. It takes some basic input from the user, suggests a list of possible destinations, lets you pick one, and then pulls up flights to that location.

Flight Search – A more focused search tool. Here, you provide specific details (like origin & destination airports, dates, and passenger info), and it returns all the flights that match your criteria — kind of like a simplified version of Google Flights!

# Important Note:

This project functions by getting flight data, through API calls, from a website called Amadeus for Developers. To do so, it uses API keys that must be kept private. To run this project locally, you would need to replace the API keys at the top of the file called ApiCalls with your own working keys. 

There are also two walkthrough files that showcase sample runs of each main program. These let you see how the programs look and behave in action. No need to set up your own API keys first!

# What I learned / Skills I demonstrated in this project

### API usage: 
I taught myself how to use and format API calls to get relevant data from sites like Amadeus for Developers.

### Working with external libraries (json, requests, time, datetime, tabulate):
&nbsp;&nbsp;&nbsp;&nbsp;**json** – Learned how to structure API request bodies and how to load/dump JSON data to and from external files for storage and retrieval (Ex: accessing & updating the airport locations file).

&nbsp;&nbsp;&nbsp;&nbsp;**requests** – Gained experience making HTTP requests to external APIs, handling parameters, headers, and parsing responses.

&nbsp;&nbsp;&nbsp;&nbsp;**time** – Used for detecting when an API token has expired and needs to be refreshed.

&nbsp;&nbsp;&nbsp;&nbsp;**datetime** – Worked with dates and times for input validation, formatting, and calculating ranges(e.g., trip durations).

&nbsp;&nbsp;&nbsp;&nbsp;**tabulate** – Learned to present data in clean, readable tables for a better user experience.

### Input Handling:
Used try/except blocks to catch invalid input and prompt the user to re-enter correct information before continuing.
Ex: In get_date() and get_duration() functions in FlightInspiration.py.

**Some functionalities related to input handling include...**

(User will be re-prompted in every one of these scenarios)

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

&nbsp;&nbsp;&nbsp;&nbsp;-When inputting traveler info, user cannot have more of one type of passenger than the total       number of passengers they selected. Ex: 3 passengers total, user selects 4 adults.

&nbsp;&nbsp;&nbsp;&nbsp;-Cannot enter 0 for all passenger types.

&nbsp;&nbsp;&nbsp;&nbsp;-If the sum of each type of passenger is less than the total number of passengers selected by the  user, they will be notified by the program and given the option to modify their traveler info or continue with the data that they already entered. Must enter either 'con' or 'mod' at this stage.

&nbsp;&nbsp;&nbsp;&nbsp;-Infants must be accompanied by at least one adult or senior.

&nbsp;&nbsp;&nbsp;&nbsp;-The number of held infants must equal the number of adults/seniors.

