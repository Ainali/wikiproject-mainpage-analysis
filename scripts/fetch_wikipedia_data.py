import requests
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from datetime import datetime, date
import os

# SPARQL query to fetch language code and main page title for each Wikipedia language
sparql_query = """
SELECT ?language_code ?mainpage_title WHERE {
  hint:Query hint:optimizer "None".
  ?link schema:about wd:Q5296 ;
        schema:name ?mainpage_title ;
        schema:inLanguage ?language_code ;
        schema:isPartOf ?wiki .
  ?wiki wikibase:wikiGroup "wikipedia".
} ORDER BY ?language_code
"""

# Function to run a SPARQL query and return results
def run_sparql_query(endpoint_url, sparql_query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

# Function to fetch the API response and extract wikibase_item values
def fetch_wikibase_items(api_url, params):
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        wikibase_items = []
        pages = data.get('query', {}).get('pages', [])
        for page in pages:
            pageprops = page.get('pageprops', {})
            wikibase_item = pageprops.get('wikibase_item')
            if wikibase_item:
                wikibase_items.append(wikibase_item)
        return wikibase_items
    else:
        print(f"Error: Unable to fetch data (status code: {response.status_code})")
        return []

# Function to construct the SPARQL query
def construct_sparql_query(wikibase_items):
    values_clause = " ".join(f"wd:{item}" for item in wikibase_items)
    sparql_query = f"""
    SELECT DISTINCT ?page ?pageLabel ?item ?itemLabel WHERE {{
    VALUES ?page {{ {values_clause} }} # This is the list the API results go into
    ?page wdt:P5008 | wdt:P6104 ?item # Use both on focus list of WikiProject and maintained by WikiProject
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }} ORDER BY ?page
    """
    return sparql_query

# Function to run the SPARQL query for fetching language codes and main page titles
def fetch_language_data():
    endpoint_url = "https://query.wikidata.org/sparql"
    results = run_sparql_query(endpoint_url, sparql_query)
    return results

# Function to create a table that counts how many times each ?item is returned, including labels
def create_count_table(results):
    items = []
    for result in results["results"]["bindings"]:
        item = result['item']['value'].split('/')[-1]  # Extract item ID
        item_label = result['itemLabel']['value'] if 'itemLabel' in result else ''  # Extract item label
        items.append((item, item_label))

    # Create a DataFrame and count occurrences
    df = pd.DataFrame(items, columns=['item', 'itemLabel'])
    count_table = df.groupby(['item', 'itemLabel']).size().reset_index(name='count')

    # Sort the table by count in descending order
    count_table = count_table.sort_values(by='count', ascending=False).reset_index(drop=True)

    return count_table

# Function to save results to a CSV file
def save_to_csv(count_table, language_code):
    year = datetime.utcnow().year
    today = datetime.utcnow().date()
    filename = f'data/results_{language_code}_{year}.csv'

    # Add date column
    count_table['date'] = today

    # Check if the file already exists
    if os.path.exists(filename):
        # Append new data to the existing file
        count_table.to_csv(filename, mode='a', header=False, index=False)
    else:
        # Create a new file and write the header
        count_table.to_csv(filename, index=False)

# Main function
def main():
    # Fetch language data (language codes and main page titles)
    results = fetch_language_data()

    # Iterate over each language
    for result in results["results"]["bindings"]:
        language_code = result['language_code']['value']
        mainpage_title = result['mainpage_title']['value']

        print(f"Processing Wikipedia in {language_code}...")

        # Construct API URL and parameters for the specific language
        api_url = f"https://{language_code}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageprops",
            "titles": mainpage_title,
            "generator": "links",
            "formatversion": 2,
            "ppcontinue": "",
            "ppprop": "wikibase_item",
            "gplnamespace": 0,
            "gpllimit": "max"
        }

        # Fetch wikibase items for the current language
        wikibase_items = fetch_wikibase_items(api_url, params)

        if wikibase_items:
            # Construct SPARQL query
            sparql_query = construct_sparql_query(wikibase_items)
            endpoint_url = "https://query.wikidata.org/sparql"

            # Run SPARQL query
            results = run_sparql_query(endpoint_url, sparql_query)

            # Create count table
            count_table = create_count_table(results)
            print(count_table)

            # Save results to CSV file
            save_to_csv(count_table, language_code)

        print(f"Processing for {language_code} completed.")
        print("=" * 50)

if __name__ == "__main__":
    main()
