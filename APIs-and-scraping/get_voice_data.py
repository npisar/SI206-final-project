#eva was here 

import requests
import json

'''
This file will call the GSHIMPACT API to get data for every voice line in the game.

The only function gets the data for all of the voice lines by the characters. It then appends all of that data to a master list.

Then, the master list is iterated through and dumped into one large json file.
'''

def get_voice(base_url, limit=25, max_requests=3):
    '''
    ARGUMENTS:
        base_url: str representing GSHIMPACT API base url
        limit=25: int. the limit of how many responses are received per request. 25 by default.
        max_requests: int. the maximum number of requests to be made to the API
    
    RETURNS:
        None
    '''
    page = 1
    all_voices = []
    for i in range(max_requests):
        resp = requests.get(f"{base_url}voices?limit={limit}&page={page}")
        print(f"now getting data on page {page}")
        if resp.status_code != 200:
            print(f"Failed to get data: {resp.status_code}")
            return None

        # convert to json and add to all data
        data = resp.json()
        voices = data['results']
        all_voices.append(voices)
        print(f"{'-'*20}\ndata on page {page} is {data}\n\n{'-'*20}")

        page += 1

    # write to the file
    with open("voice-data.json", "w") as file:
        all_voices = [voices for page in all_voices for voices in page]
        json.dump(all_voices, file, indent=4)



def main():
    get_voice(base_url="https://gsi.fly.dev/", limit=25, max_requests=2)

main()