import requests
import json

'''
This file will call the Unofficial Genshin API to get data for every character in the game.

The first function gets a list of the character names to be iterated through, and the second function iterates through that list, grabs the data from each character's url, and adds all of that data to a master list.

Then, the master list is iterated through and dumped into one large json file.
'''

def get_character_names(base_url):
    '''
    ARGUMENTS:
        base_url: str representing GSHIMPACT API base url
    
    RETURNS:
        all_character_names, a list of all of the character names taken from the API
    '''
    all_character_names = []
    resp = requests.get(f"{base_url}characters/")
    if resp.status_code != 200:
        print(f"Failed on get_character_names")
        print(f"Failed to get data: {resp.status_code}")
        return []

    # convert to json and add to all characters list
    data = resp.json()
    for character in data['characters']:    
        all_character_names.append(character)
    
    return all_character_names


def get_character_info(base_url, character_names_list):
    '''
    ARGUMENTS:
        base_url: str. same base as used 
        character_names_list: a list of strings representing characters names, gotten from get_characters
    
    RETURNS: None
    '''
    all_character_data = []
    for character in character_names_list:
        resp = requests.get(f"{base_url}character/{character}/")
        if resp.status_code != 200:
            print(f"Failed on get_character_info")
            print(f"Failed to get data: {resp.status_code}")
    
        character_data_json = resp.json()
        all_character_data.append(character_data_json)


    # write to the file
    with open("character-data.json", "w") as file:
        all_characters = [character for character in all_character_data]
        json.dump(all_characters, file, indent=4)



def main():
    character_list = get_character_names(base_url="https://genshin-impact.up.railway.app/")

    get_character_info(base_url="https://genshin-impact.up.railway.app/", character_names_list=character_list)

main()