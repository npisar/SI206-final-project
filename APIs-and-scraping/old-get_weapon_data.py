import requests
import json

'''
This file will call the Genshin API hosted on https://genshin-api.netlify.app/api/ to get data for every weapon in the game.

# The function calls the url and gets all of the wepons in the game
'''

def get_weapon_info(base_url):
    '''
    ARGUMENTS:
        base_url: str representing Genshin.dev API base url
    
    RETURNS:
        all_weapon_names, a list of all of the weapon names taken from the API
    '''
    all_weapon_data = []
    resp = requests.get(f"{base_url}/weapons/")
    if resp.status_code != 200:
        print(f"Failed on get_weapon_names")
        print(f"Failed to get data: {resp.status_code}")
        return []

    # convert to json and add to all weapons list
    data = resp.json()
    for weapon in data:    
        all_weapon_data.append(weapon)

    # write to the file
    with open("weapon-data.json", "w") as file:
        all_weapons = [weapon for weapon in all_weapon_data]
        json.dump(all_weapons, file, indent=4)



def main():
    get_weapon_info(base_url="https://genshinlist.com/api")

main()