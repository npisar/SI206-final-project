

import requests
import json

'''
This file will call the GSHIMPACT API to get data for every character in the game.

The only function gets the data for all of the set number of characters on a page. It then appends all of that data to a master list.

Then, the master list is iterated through and dumped into one large json file.
'''

def get_characters(base_url, limit=25, max_requests=2):
    '''
    ARGUMENTS:
        base_url: str representing GSHIMPACT API base url
        limit=25: int. the limit of how many responses are received per request. 25 by default.
        max_requests: int. the maximum number of requests to be made to the API
    
    RETURNS:
        None
    '''
    page = 1
    all_characters = []
    for i in range(max_requests):
        resp = requests.get(f"{base_url}characters?limit={limit}&page={page}")
        # print(f"now getting data on page {page}")
        if resp.status_code != 200:
            print(f"Failed to get data: {resp.status_code}")
            return None

        # convert to json and add to all data
        data = resp.json()
        characters = data['results']
        all_characters.append(characters)
        # print(f"{'-'*20}\ndata on page {page} is {data}\n\n{'-'*20}")

        # stop when the number of items is less than the limit
        # print(f"len data results is {len(data['results'])"}
        if len(data['results']) < limit:
            break
        page += 1

    # write to the file
    with open("character-data.json", "w") as file:
        all_characters = [character for page in all_characters for character in page]
        json.dump(all_characters, file, indent=4)



def main():
    get_characters(base_url="https://gsi.fly.dev/", limit=25, max_requests=2)

main()