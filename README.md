# Travel Inspiration Helper
✈️Find your next dream destination—and the flight to take you there!

This project comes with two main programs:

Flight Inspiration – A tool for when you've got the travel bug and some vacation time, but you’re not sure where to go. It takes some basic input from the user, suggests a list of possible destinations, lets you pick one, and then pulls up flights to that location.

Flight Search – A more focused search tool. Here, you provide specific details (like origin & destination airports, dates, and passenger info), and it returns all the flights that match your criteria — kind of like a simplified version of Google Flights!

# Important Note:

This project functions by getting flight data, through API calls, from a website called Amadeus for Developers. To do so, it uses API keys that must be kept private. To run this project locally, you would need to replace the API keys at the top of the file called ApiCalls with your own working keys. 

There are also two walkthrough files that showcase sample runs of each main program. These let you see how the programs look and behave in action. No need to set up your own API keys first!

# What I learned / Skills I demonstrated in this project

API usage: I taught myself how to use and format API calls to get relevant data from sites like Amadeus for Developers.

Working with external libraries (json, requests, time, datetime, tabulate):

  json – Learned how to structure API request bodies and how to load/dump JSON data to and from external files for storage    and retrieval (Ex: accessing & updating the airport locations file).
  
  requests – Gained experience making HTTP requests to external APIs, handling parameters, headers, and parsing               responses.
  
  time – Used for detecting when an API token has expired and needs to be refreshed.
  
  datetime – Worked with dates and times for input validation, formatting, and calculating ranges (e.g., trip durations).
  
  tabulate – Learned to present data in clean, readable tables for a better user experience.

