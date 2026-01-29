import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# Configuration
base_url = "https://phenotypes.healthdatagateway.org"
list_url_template = "https://phenotypes.healthdatagateway.org/phenotypes/?collections=21&page={}&page_size=3"

phenotypes_to_process = []


for page_num in range(1, 5): 
    print(f"Scanning page {page_num}...")
    
    # 1. Request the list page
    response = requests.get(list_url_template.format(page_num))
    
    if response.status_code != 200:
        print(f"Stopping: Failed to load page {page_num}")
        break
        
    # 2. Parse the HTML
    soup = BeautifulSoup(response.content, "html.parser")
    
    # 3. Find all links that look like /phenotypes/PH.../version/.../detail/

    links = soup.find_all('a', href=True)
    
    found_on_page = 0
    for link in links:
        href = link['href']
        
        match = re.search(r'/phenotypes/(PH\d+)/version/(\d+)/detail', href)
        
        if match:
            p_id = match.group(1)
            p_version = match.group(2)
            
            
            p_name = link.text.strip()
            
           
            if not any(d['id'] == p_id for d in phenotypes_to_process):
                phenotypes_to_process.append({
                    'id': p_id,
                    'version': p_version,
                    'name': p_name
                })
                found_on_page += 1

    print(f"Found {found_on_page} new phenotypes on page {page_num}.")
    time.sleep(1) 

print(f"\nTotal phenotypes found: {len(phenotypes_to_process)}")
print(phenotypes_to_process[:5]) 

all_icd_codes = []

print(f"Starting API downloads for {len(phenotypes_to_process)} phenotypes...")

for index, pheno in enumerate(phenotypes_to_process):
    p_id = pheno['id']
    p_ver = pheno['version']
    p_name = pheno['name']
    
    # Construct the API URL based on your provided format
    api_url = f"http://phenotypes.healthdatagateway.org/api/v1/phenotypes/{p_id}/version/{p_ver}/export/codes/?format=json"
    
    try:
        # Request the JSON data directly
        r = requests.get(api_url)
        
        if r.status_code == 200:
            data = r.json()
            
            # The API usually returns a list of all codes (ReadV2, ICD10, etc.)
            # We need to loop through them and find the ICD10 ones.
            
            
            for item in data:
                # We check common fields for the code type. 
                # Adjust 'coding_system' or 'vocabulary' if the column name is different in the final Excel.
                # We convert whole row to string to search for "ICD" if unsure of column name.
                row_str = str(item).upper()
                
                # Check if it looks like an ICD-10 entry
                
                
                # We will save everything that mentions ICD10
                if "ICD10" in row_str or "ICD-10" in row_str:
                    item['Disease_Name'] = p_name
                    item['Phenotype_ID'] = p_id
                    item['Version'] = p_ver
                    all_icd_codes.append(item)
                    
        else:
            print(f"Failed to fetch data for {p_id}")
            
    except Exception as e:
        print(f"Error processing {p_id}: {e}")

    # Progress tracker
    if (index + 1) % 10 == 0:
        print(f"Processed {index + 1} phenotypes...")
    
    # Small delay to prevent blocking
    time.sleep(0.5)

print(f"\nFinished! Extracted {len(all_icd_codes)} ICD-10 code entries.")
