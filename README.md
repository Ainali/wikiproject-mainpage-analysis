# WikiProject Mainpage Analysis

This tool shows the number of links from the mainpage of Wikipedia to an article connected to a WikiProject.

It runs via a GitHub action daily and adds data to a CSV file, one per language and year.

First the script checks for main pages through a SPARQL query. Then for each of those, an API call is made to get the Wikidata IDs for all links to the main namespace. Then these are plugged into another SPARQL query to see to which, if any, WikiProject they are connected to. The result is appended to the CSV file. 

A summary table is simply published via GitHub pages.

The aggregation is done in the browser when the user has made a selection.
