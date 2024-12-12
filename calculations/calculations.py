import sqlite3
import os

def calculate_average_weapon_damage_per_rarity(cur):
    '''
    ARGUMENTS:
    cur:
        SQLite cursor
    
    RETURNS:
        rarity_and_avg_attack: dict
            The keys are integers representing weapon rarity, and the values are floats representing average damage for weapons of that rarity
    '''
    cur.execute(
        '''
        SELECT id, rarity, base_attack FROM Weapons
        '''
    )
    rows = cur.fetchall()
    weapon_data = [{'id':row[0], 'rarity':row[1], 'base_attack':row[2]} for row in rows]
    # print(f"rows is {rows}")

    rarity_dict = {}
    for rarity in range(1, 6):
        rarity_match_list = [i for i in weapon_data if i['rarity'] == rarity]
        rarity_dict[rarity] = rarity_match_list

    # debug print 
    # for k, v in rarity_dict.items():
    #     print(f"rarity dict for rarity {k} is")
    #     print(f"{v}")
    #     print(f"{'-'*30}\n")

    rarity_and_avg_attack = {}
    for rarity in range(1, 6):
        rarity_attack_sum = 0
        rarity_count = len(rarity_dict[rarity])

        for entry in rarity_dict[rarity]:
            entry_attack = entry['base_attack']
            rarity_attack_sum += entry_attack
        
        rarity_and_avg_attack[rarity] = "{:04.2f}".format(rarity_attack_sum / rarity_count)

    # debug print    
    # for k,v in rarity_and_avg_attack.items():
    #     print(f"avg attack for rarity {k} is")
    #     print(f"{v}")
    #     print(f"{'-'*30}\n")
    # print(f"\n\n\n")
    return rarity_and_avg_attack

def calculate_difference_awdpr(awdpr):
    '''
    ARGUMENTS:
    awdpr: dict
        Dictionary of average weapon damage per rarity returned from calculate_average_weapon_damage_per_rarirty 

    RETURNS:
    difference_awdpr: list of dicts
        List of dicts where the keys are each rarity, and the values are a list of calculations comparing the difference between the average damages for each rarity (ignoring the difference between a rarity and itself)
    '''
    difference_awdpr = []
    for p_i in range(1, 6):
        calcs = {p_i: []} 
        
        for n_i in range(5, 0, -1):
            calc_name = f"{n_i}-{p_i}"
            calc = "{:04.2f}".format(float(awdpr[n_i]) - float(awdpr[p_i]))
            if not calc == '0.00':
                calcs[p_i].append({calc_name: calc})
        difference_awdpr.append(calcs)
    
    # debug print    
    # for calcs_d in difference_awdpr:
    #     for k,v in calcs_d.items():
    #         print(f"calcs list for rarity {k} is")
    #         print(f"{v}")
    #         print(f"{'-'*30}\n")
    # print(f"\n\n\n")
    return difference_awdpr













def calculate_average_weapon_damage_per_type(cur):
    '''
    ARGUMENTS:
    cur:
        SQLite cursor
    
    RETURNS:
    rarity_and_avg_attack: dict
        Dict where the keys are integers representing weapon type, and the values are floats representing average damage for weapons of that type
    '''
    cur.execute(
        '''
        SELECT weapons.id, weapontypes.weapon_type, weapons.base_attack
        FROM Weapons JOIN WeaponTypes
        ON Weapons.weapon_type_id = WeaponTypes.id
        '''
    )
    rows = cur.fetchall()
    weapon_data = [{'id':row[0], 'weapon_type':row[1], 'base_attack':row[2]} for row in rows]
    # print(f"rows is {rows}")
    # print(f"weapon_data is {weapon_data}")

    weapon_types = []
    for weapon in weapon_data:
        if weapon['weapon_type'] not in weapon_types:
            weapon_types.append(weapon['weapon_type'])
        if len(weapon_types) == 5:
            break
        else:
            continue
    # print(f"weapon types is {weapon_types}")
    
    type_dict = {}
    for w_type in weapon_types:
        type_match_list = [i for i in weapon_data if i['weapon_type'] == w_type]
        type_dict[w_type] = type_match_list
    # print(f"type dict is {type_dict}")
    # debug print    
    # for k, v in type_dict.items():
    #     print(f"type dict for type {k} is")
    #     print(f"{v}")
    #     print(f"{'-'*30}\n")

    type_and_avg_attack = {}
    for w_type in weapon_types:
        type_attack_sum = 0
        type_count = len(type_dict[w_type])

        for entry in type_dict[w_type]:
            entry_attack = entry['base_attack']
            type_attack_sum += entry_attack
        
        type_and_avg_attack[w_type] = "{:04.2f}".format(type_attack_sum / type_count)

    # debug print    
    # for k,v in type_and_avg_attack.items():
    #     print(f"avg attack for type {k} is")
    #     print(f"{v}")
    #     print(f"{'-'*30}\n")
    # print(f"\n\n\n")
    return (type_and_avg_attack, weapon_types)

def calculate_difference_awdpt(awdpt, weapon_types):
    '''
    ARGUMENTS:
    awdpt: dict
        Dictionary of average weapon damage per type returned from calculate_average_weapon_damage_per_type
    weapon_types: list
        List of weapon types returned from calculate_average_weapon_damage_per_type

    RETURNS:
    difference awdpr: list of dicts
        Keys are each weapon type, and the values are a list of calculations comparing the difference between the average damages for each type (ignoring the difference between a type and itself)
    '''
    difference_awdpt = []
    for main_type in weapon_types:
        calcs = {main_type: []} 
        
        for secondary_type in weapon_types:
            calc_name = f"{secondary_type}-{main_type}"
            calc = "{:04.2f}".format(float(awdpt[secondary_type]) - float(awdpt[main_type]))
            if not calc == '0.00':
                calcs[main_type].append({calc_name: calc})
            elif calc == '0.00' and not main_type == secondary_type:
                calcs[main_type].append({calc_name: calc})
        difference_awdpt.append(calcs)
    
    # debug print    
    # for calcs_d in difference_awdpt:
    #     for k,v in calcs_d.items():
    #         print(f"calcs list for type {k} is")
    #         print(f"{v}")
    #         print(f"{'-'*30}\n")
    # print(f"\n\n\n")
    return difference_awdpt


















def calculate_num_artifacts_per_quality(cur):
    '''
    ARGUMENTS:
    cur:
        SQLite cursor
    
    RETURNS:
        num_artifacts_per_quality: dict
        Dict where the  keys are integers representing artifact max quality, and the values are ints representing the count for artifacts of that max rarity
    '''
    cur.execute(
        '''
        SELECT id, max_set_quality FROM Artifacts
        '''
    )
    rows = cur.fetchall()
    artifact_data = [{'id':row[0], 'max_set_quality':row[1]} for row in rows]

    quality_dict = {}
    for quality in range(1, 6):
        quality_match_list = [i for i in artifact_data if i['max_set_quality'] == quality]
        quality_dict[quality] = quality_match_list

    # debug print    
    # for k, v in quality_dict.items():
    #     print(f"rarity dict for rarity {k} is")
    #     print(f"{v}")
    #     print(f"{'-'*30}\n")

    quality_and_count = {}
    for quality in range(1, 6):
        quality_count = len(quality_dict[quality])
        
        quality_and_count[quality] = quality_count

    # debug print    
    # for k,v in quality_and_count.items():
    #     print(f"count for quality {k} is")
    #     print(f"{v}")
    #     print(f"{'-'*30}\n")
    # print(f"\n\n\n")
    return quality_and_count

def calculate_num_media_per_character(cur):
    cur.execute(
    '''
    SELECT
        Characters.name,
        Media.promotion + Media.holiday + Media.birthday + Media.videos + Media.cameos + Media.artwork AS sum_of_media_values
    FROM Media JOIN Characters
    ON Media.character_id = Characters.id
    '''
    )
    rows = cur.fetchall()
    media_data = [{row[0]:row[1]} for row in rows]

    cur.execute(
    '''
    SELECT name FROM Characters
    '''
    )
    all_characters = cur.fetchall()
    all_character_names = [row[0] for row in all_characters]

    # Creating a set of character names that already exist in media_data
    existing_characters = {list(char_dict.keys())[0] for char_dict in media_data}

    # Adding characters that are not present in media_data
    for name in all_character_names:
        if name not in existing_characters:
            media_data.append({name: 0})

    # Sort the media_data list by character names
    media_data = sorted(media_data, key=lambda d: list(d.keys())[0])

    return media_data










def main():
    # create the connection and cursor
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "..")) 
    db_path = os.path.join(root_dir, 'genshin_impact_data.db')
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Call the functions to perform calculations
    awdpr = calculate_average_weapon_damage_per_rarity(cur)
    difference_awdpr = calculate_difference_awdpr(awdpr)
    awdpt, weapon_types = calculate_average_weapon_damage_per_type(cur)
    difference_awdpt = calculate_difference_awdpt(awdpt, weapon_types)
    num_artifacts_per_quality = calculate_num_artifacts_per_quality(cur)
    num_media_per_character = calculate_num_media_per_character(cur)

    # Write the results to calculations.txt file
    with open('calculations/calculations.txt', 'w') as file:

        # Average weapon damage per rarity
        file.write("FUNCTION / CALCULATION 1:\nAverage Weapon Damage Per Rarity:\n\n")
        file.write("This section shows the average base attack for weapons of each rarity (1 to 5 stars).\n")
        for rarity, avg_attack in awdpr.items():
            file.write(f"    Rarity {rarity}: {avg_attack}\n")
        file.write(f"{'-'*30}\n\n\n")

        # Difference in average weapon damage per rarity
        file.write(f"{'-'*30}\n")
        file.write("FUNCTION / CALCULATION 2:\nDifference in Average Weapon Damage Per Rarity:\n\n")
        file.write("These calculations show the difference in average base attack between weapons of different rarities.\n")
        for difference in difference_awdpr:
            for rarity, calcs in difference.items():
                file.write(f"    Rarity {rarity} differences:\n")
                for calc in calcs:
                    for calc_name, value in calc.items():
                        file.write(f"        {calc_name}: {value}\n")
        file.write(f"{'-'*30}\n\n\n")

        # Average weapon damage per type
        file.write(f"{'-'*30}\n")
        file.write("FUNCTION / CALCULATION 3:\nAverage Weapon Damage Per Type:\n\n")
        file.write("This section shows the average base attack for each weapon type.\n")
        for w_type, avg_attack in awdpt.items():
            file.write(f"    Weapon Type {w_type}: {avg_attack}\n")
        file.write(f"{'-'*30}\n\n\n")

        # Difference in average weapon damage per type
        file.write(f"{'-'*30}\n")
        file.write("FUNCTION / CALCULATION 4:\nDifference in Average Weapon Damage Per Type:\n\n")
        file.write("These calculations show the difference in average base attack between different weapon types.\n")
        for difference in difference_awdpt:
            for weapon_type, calcs in difference.items():
                file.write(f"    Weapon Type {weapon_type} differences:\n")
                for calc in calcs:
                    for calc_name, value in calc.items():
                        file.write(f"        {calc_name}: {value}\n")
        file.write(f"{'-'*30}\n\n\n")

        # Number of artifacts per quality
        file.write(f"{'-'*30}\n")
        file.write("FUNCTION / CALCULATION 5:\nNumber of Artifacts Per Quality:\n\n")
        file.write("This section shows the count of artifacts for each max quality (1 to 5 stars).\n")
        for quality, count in num_artifacts_per_quality.items():
            file.write(f"    Max Quality {quality}: {count}\n")
        file.write(f"{'-'*30}\n\n\n")

        # Number of media per character
        file.write(f"{'-'*30}\n")
        file.write("FUNCTION / CALCULATION 6:\nNumber of Media Appearances Per Character:\n\n")
        file.write("This section shows the total media appearances (promotion, holiday, birthday, videos, cameos, artwork) for each character.\n")
        for media in num_media_per_character:
            for character, count in media.items():
                file.write(f"    Character {character}: {count}\n")
        file.write(f"{'-'*30}\n\n\n")

    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()