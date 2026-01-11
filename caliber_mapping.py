import requests
from bs4 import BeautifulSoup
import urllib.parse

# Define the base URL
base_url = "https://phenotypes.healthdatagateway.org/phenotypes/?collections=21&page="

# Number of pages to scrape
num_pages = 16

# Initialize an empty list to store the URLs
urls = []

# Iterate through the pages
for page_num in range(1, num_pages):
    url = base_url + str(page_num)
    
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find all anchor tags (<a>) with href attributes
            href_links = soup.find_all("a", href=True)
            
            # Extract and add links starting with "/phenotypes/" to the 'urls' list
            for link in href_links:
                href = link.get("href")
                if href.startswith("/phenotypes/"):
                    # Combine the relative link with the base URL
                    full_link = urllib.parse.urljoin(url, href)
                    
                    # Replace 'detail/' with 'export/codes/'
                    modified_link = full_link.replace('detail/', 'export/codes/')
                    urls.append(modified_link)
                    
        else:
            print(f"Failed to fetch data from URL: {url}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data from URL {url}: {e}")

# Print the collected URLs
#for url in urls:
#    print(url)

# URL to remove
url_to_remove = 'https://phenotypes.healthdatagateway.org/phenotypes/'

# Remove the specific URL from the list
urls = [url for url in urls if url != url_to_remove]


import pandas as pd
import requests
from io import StringIO

# Initialize an empty list to store DataFrames
dfs = []

# Iterate through the URLs and fetch CSV data
for url in urls:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Assuming the content is CSV data, parse it into a DataFrame
            csv_data = response.text
            df_cc = pd.read_csv(StringIO(csv_data))
            dfs.append(df_cc)
        else:
            print(f"Failed to fetch data from URL: {url}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data from URL {url}: {e}")

# Concatenate the DataFrames into a single DataFrame
concatenated_df = pd.concat(dfs, ignore_index=True)

# Print the concatenated DataFrame
#print(concatenated_df)

columns_to_keep = ['phenotype_id','phenotype_name','concept_id','concept_name','code','coding_system']

concatenated_df_refined = concatenated_df[columns_to_keep]

#ICD10 codes for all pages - ICD10 codes

df_ICD10 = concatenated_df_refined[(concatenated_df_refined.coding_system == 'ICD10 codes')]

df_ICD10 = df_ICD10.drop_duplicates(subset='code')
df_ICD10_selected = df_ICD10[['phenotype_id', 'code']]

df_ICD10_selected.rename(columns={'phenotype_id': 'Caliber', 'code': 'ICD10'}, inplace=True)

df_ICD10_selected['ICD10'] = df_ICD10_selected['ICD10'].str.replace('.', '')

icd10_to_caliber_map = dict(zip(df_ICD10_selected['ICD10'], df_ICD10_selected['Caliber']))
df['Caliber'] = df['ICD10'].map(icd10_to_caliber_map)
