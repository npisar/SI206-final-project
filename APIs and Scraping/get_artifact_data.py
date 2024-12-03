import requests
import json

'''
This file will call the Genshin.dev API to get data for every character in the game.

# The first function gets a list of the character names to be iterated through, and the second function iterates through that list, grabs the data from each character's url, and adds all of that data to a master list.

# Then, the master list is iterated through and dumped into one large json file.
'''

def get_artifacts(base_url):
    '''
    ARGUMENTS:
        base_url: str representing Genshin API base url
    
    RETURNS:
        all_character_names, a list of all of the character names taken from the API
    '''
    all_artifact_names = []
    resp = requests.get(f"{base_url}artifacts/")
    if resp.status_code != 200:
        print(f"Failed on get_character_names")
        print(f"Failed to get data: {resp.status_code}")
        return []

    # convert to json and add to all characters list
    data = resp.json()
    for character in data:    
        all_artifact_names.append(character)
    
    return all_artifact_names


# def get_character_info(base_url, character_names_list):
#     '''
#     ARGUMENTS:
#         base_url: str. same base as used 
#         character_names_list: a list of strings representing characters names, gotten from get_characters
    
#     RETURNS: None
#     '''
#     all_character_data = []
#     for character in character_names_list:
#         resp = requests.get(f"{base_url}characters/{character}/")
#         if resp.status_code != 200:
#             print(f"Failed on get_character_info")
#             print(f"Failed to get data: {resp.status_code}")
    
#         character_data_json = resp.json()
#         all_character_data.append(character_data_json)


#     # write to the file
#     with open("character-data.json", "w") as file:
#         all_characters = [character for character in all_character_data]
#         json.dump(all_characters, file, indent=4)



def main():
    artifact_list = get_artifacts(base_url="https://api-dev.rojoinferno.com/genshin-api/v1/")

    get_character_info(base_url="https://api-dev.rojoinferno.com/genshin-api/v1/", character_names_list=character_list)

main()