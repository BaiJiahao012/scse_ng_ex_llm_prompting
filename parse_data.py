###########################################################
# parse_data.py
###########################################################

import json
import os

## Logic for loading and reading from a JSON file. 
## The function must return only the items
def load_items(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    # Return only the list of items
    return data["items"]


## Logic for getting only those items that are not yet claimed 
## It should return only the items that are unclaimed
def get_unclaimed_items(items):
    unclaimed_list = []
    
    for item in items:
        # Check if the status is unclaimed
        if item["status"] == "unclaimed":
            unclaimed_list.append(item)
            
    return unclaimed_list


## Logic to save the result to a JSON file.
## The function should create the directory if it does not exist and save the result in a JSON format.
def save_result(result, filename):
    # Extract the directory path from the filename
    directory = os.path.dirname(filename)
    
    # Check if a directory is specified and if it doesn't exist
    if directory:
        if not os.path.exists(directory):
            os.makedirs(directory)
            
    # Save the result to the JSON file
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(result, file, indent=4)


