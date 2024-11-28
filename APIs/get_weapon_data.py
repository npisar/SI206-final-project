import requests
import json

'''
This file will call the Genshin API to get data for every weapon in the game.

# The first function gets a list of the character names to be iterated through, and the second function iterates through that list, grabs the data from each character's url, and adds all of that data to a master list.

# Then, the master list is iterated through and dumped into one large json file.
'''

def get_weapon_info(base_url):
    '''
    ARGUMENTS:
        base_url: str representing GSHIMPACT API base url
    
    RETURNS:
        all_character_names, a list of all of the character names taken from the API
    '''
    all_weapons = []
    resp = requests.get(f"{base_url}weapons?infoDataSize=all")
    if resp.status_code != 200:
        print(f"Failed on get_weapon_info")
        print(f"Failed to get data: {resp.status_code}")
        return []

    # convert to json and add to all characters list
    data = resp.json()
    all_weapons.append(data)


    with open("weapon-data.json", "w") as file:
        all_weapons = [weapon for weapon in all_weapons]
        json.dump(all_weapons, file, indent=4)



def main():
    get_weapon_info(base_url="https://genshin-app-api.herokuapp.com/api/")

main()