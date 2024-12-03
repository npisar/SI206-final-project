import requests
import json

'''
This file will call the Genshin.dev API to get data for every weapon in the game.

# The first function gets a list of the weapon names to be iterated through, and the second function iterates through that list, grabs the data from each weapon's url, and adds all of that data to a master list.

# Then, the master list is iterated through and dumped into one large json file.
'''

def get_weapon_names(base_url):
    '''
    ARGUMENTS:
        base_url: str representing Genshin.dev API base url
    
    RETURNS:
        all_weapon_names, a list of all of the weapon names taken from the API
    '''
    all_weapon_names = []
    resp = requests.get(f"{base_url}weapons/")
    if resp.status_code != 200:
        print(f"Failed on get_weapon_names")
        print(f"Failed to get data: {resp.status_code}")
        return []

    # convert to json and add to all weapons list
    data = resp.json()
    for weapon in data:    
        all_weapon_names.append(weapon)
    
    return all_weapon_names


def get_weapon_info(base_url, weapon_names_list):
    '''
    ARGUMENTS:
        base_url: str. same base as used 
        weapon_names_list: a list of strings representing weapons names, gotten from get_weapons
    
    RETURNS: None
    '''
    all_weapon_data = []
    for weapon in weapon_names_list:
        resp = requests.get(f"{base_url}weapons/{weapon}/")
        if resp.status_code != 200:
            print(f"Failed on get_weapon_info")
            print(f"Failed to get data: {resp.status_code}")
    
        weapon_data_json = resp.json()
        all_weapon_data.append(weapon_data_json)


    # write to the file
    with open("weapon-data.json", "w") as file:
        all_weapons = [weapon for weapon in all_weapon_data]
        json.dump(all_weapons, file, indent=4)



def main():
    weapon_list = get_weapon_names(base_url="https://genshin.jmp.blue/")

    get_weapon_info(base_url="https://genshin.jmp.blue/", weapon_names_list=weapon_list)

main()