import requests
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from datetime import datetime

# Define the URL for the API call
url = "https://sv.wikipedia.org/w/api.php"

# Define the parameters for the API call of all links at the mainpage
params = {
    "action": "query",
    "format": "json",
    "prop": "pageprops",
    "titles": "Portal:Huvudsida",
    "generator": "links",
    "formatversion": 2,
    "ppcontinue": "",
    "ppprop": "wikibase_item",
    "gplnamespace": 0,
    "gpllimit": "max"
}

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

# Function to run the SPARQL query and return results
def run_sparql_query(endpoint_url, sparql_query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
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

# Main code
wikibase_items = fetch_wikibase_items(url, params)
if wikibase_items:
    sparql_query = construct_sparql_query(wikibase_items)
    endpoint_url = "https://query.wikidata.org/sparql"
    results = run_sparql_query(endpoint_url, sparql_query)
    
    # Create and display the count table
    count_table = create_count_table(results)
    print(count_table)
    
    # Save results to a CSV file
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')
    count_table.to_csv(f'data/results_{timestamp}.csv', index=False)
