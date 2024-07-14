# WikiProject Mainpage Analysis

This tool shows the number of links from the mainpage of Wikipedia to an article connected to a WikiProject.

## How it works

It runs via a GitHub action daily and adds data to CSV files, one per language and year.

### Getting main page data

First the script gets all mainpages through a SPARQL query that collects all Wikipedia sitelinks on the item [Q5296](https://www.wikidata.org/wiki/Q5296) (and the language codes of those wikis).
Then for each of those, an API call is made to get the Wikidata IDs for all links from the mainpage to articles in the main namespace. Example for Swedish Wikipedia:

`https://sv.wikipedia.org/w/api.php?action=query&format=json&prop=pageprops&titles=Portal%3AHuvudsida&generator=links&formatversion=2&ppcontinue=&ppprop=wikibase_item&gplnamespace=0&gpllimit=max`
[Try it!](https://sv.wikipedia.org/w/api.php?action=query&format=json&prop=pageprops&titles=Portal%3AHuvudsida&generator=links&formatversion=2&ppcontinue=&ppprop=wikibase_item&gplnamespace=0&gpllimit=max)

### Find WikiProject connections

The Wikidata IDs are plugged into another SPARQL query to see to which, if any, WikiProjects they are connected to.
A connection is considered to exist if the items have a value for either of the Wikidata properties [on focus list of Wikimedia project (P5008)](https://www.wikidata.org/wiki/Property:P5008) or [maintained by WikiProject (P6104)](https://www.wikidata.org/wiki/Property:P6104).

### Summarize

The result is appended to a CSV file, with one line per WikiProject, the number of links for each of those and the retrieve date.

A summary table with filters for year, language and WikiProject is published via GitHub pages.

The aggregation is done in the browser when the user has made a selection.

## License

The code is under [GPL V3](LICENSE).

All data in the data folder is dedicated to the public domain, marked by [CC0 1.0](http://creativecommons.org/publicdomain/zero/1.0), which allows users worldwide to distribute, remix, adapt, and build upon the data in any medium or format, with no legal conditions on reuse. 
Attribution is suggested as "Data from the [WikiProject Mainpage Analysis](https://github.com/Ainali/wikiproject-mainpage-analysis)".
