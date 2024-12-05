import json
'''
example calcs:

WEAPONS:
    Average weapon damage for each weapon rarity?
        What is the difference between the averages? Are there diminishing returns going for rarer and rarer weapons?
    Average weapon damage for each weapon type?

ARTIFACTS:
    How many artifacts are there for each max set quality?

'''


def calculate_average_weapon_damage_per_rarity(filepath):
    '''
    ARGUMENTS:
        filepath: str representing filepath to weapon data (will be changed later)
    
    RETURNS:
        rarity_and_avg_attack: dict, with keys being integers representing weapon rarity and values being floats representing average damage for weapons of that rarity
    '''
    
    with open (filepath, "r") as weapon_data:
        weapons = json.load(weapon_data)
        # print(weapons)
        # print(len(weapons))

    rarity_dict = {}
    for rarity in range(1, 6):
        rarity_match_list = [i for i in weapons if i['rarity'] == rarity]
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
            entry_attack = entry['baseAttack']
            rarity_attack_sum += entry_attack
        
        rarity_and_avg_attack[rarity] = "{:04.2f}".format(rarity_attack_sum / rarity_count)

    # debug print    
    for k,v in rarity_and_avg_attack.items():
        print(f"avg attack for rarity {k} is")
        print(f"{v}")
        print(f"{'-'*30}\n")
    print(f"\n\n\n")
    return rarity_and_avg_attack

def calculate_difference_awdpr(awdpr):
    '''
    ARGUMENTS:
        awdpr: dict returned from calculate_average_weapon_damage_per_rarirty 

    RETURNS:
        difference awdpr: list of dicts, where the keys are each rarity, and the values are a list of calculations comparing the difference between the average damages for each rarity (ignoring the difference between a rarity and itself)
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
    for calcs_d in difference_awdpr:
        for k,v in calcs_d.items():
            print(f"calcs list for rarity {k} is")
            print(f"{v}")
            print(f"{'-'*30}\n")
    print(f"\n\n\n")
    return difference_awdpr



def calculate_average_weapon_damage_per_type(filepath):
    '''
    ARGUMENTS:
        filepath: str representing filepath to weapon data (will be changed later)
    
    RETURNS:
        rarity_and_avg_attack: dict, with keys being integers representing weapon type and values being floats representing average damage for weapons of that type
    '''
    
    with open (filepath, "r") as weapon_data:
        weapons = json.load(weapon_data)
        # print(weapons)
        # print(len(weapons))

    weapon_types = ["Bow", "Catalyst", "Claymore", "Polearm", "Sword"]
    type_dict = {}
    for type in weapon_types:
        type_match_list = [i for i in weapons if i['type'] == type]
        type_dict[type] = type_match_list

    # debug print    
    # for k, v in type_dict.items():
    #     print(f"type dict for type {k} is")
    #     print(f"{v}")
    #     print(f"{'-'*30}\n")

    type_and_avg_attack = {}
    for type in weapon_types:
        type_attack_sum = 0
        type_count = len(type_dict[type])

        for entry in type_dict[type]:
            entry_attack = entry['baseAttack']
            type_attack_sum += entry_attack
        
        type_and_avg_attack[type] = "{:04.2f}".format(type_attack_sum / type_count)

    # debug print    
    for k,v in type_and_avg_attack.items():
        print(f"avg attack for type {k} is")
        print(f"{v}")
        print(f"{'-'*30}\n")
    print(f"\n\n\n")
    return type_and_avg_attack

def calculate_difference_awdpt(awdpt):
    '''
    ARGUMENTS:
        awdpt: dict returned from calculate_average_weapon_damage_per_type

    RETURNS:
        difference awdpr: list of dicts, where the keys are each type, and the values are a list of calculations comparing the difference between the average damages for each type (ignoring the difference between a type and itself)
    '''
    difference_awdpt = []
    weapon_types = ["Bow", "Catalyst", "Claymore", "Polearm", "Sword"]
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
    for calcs_d in difference_awdpt:
        for k,v in calcs_d.items():
            print(f"calcs list for type {k} is")
            print(f"{v}")
            print(f"{'-'*30}\n")
    print(f"\n\n\n")
    return difference_awdpt


def calculate_num_artifacts_per_quality(filepath):
    '''
    ARGUMENTS:
        filepath: str representing filepath to artifact data (will be changed later)
    
    RETURNS:
        num_artifacts_per_quality: dict, with keys being integers representing artifact max quality and values being ints representing the count for artifacts of that max rarity
    '''
    
    with open (filepath, "r") as artifact_data:
        artifacts = json.load(artifact_data)

    quality_dict = {}
    for quality in range(1, 6):
        quality_match_list = [i for i in artifacts if i['maxSetQuality'] == quality]
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
    for k,v in quality_and_count.items():
        print(f"count for quality {k} is")
        print(f"{v}")
        print(f"{'-'*30}\n")
    print(f"\n\n\n")
    return quality_and_count



def main():
    print(f"\n\n{'#'*30} Weapon Damage per Rarity {'#'*30}")
    average_weapon_damage_per_rarity = calculate_average_weapon_damage_per_rarity("JSON-and-old-cache-method/weapon-data.json")
    calculate_difference_awdpr(average_weapon_damage_per_rarity)

    print(f"{'#'*91}\n{'#'*91}\n{'#'*91}\n")

    print(f"{'#'*30} Weapon Damage per Weapon Type {'#'*30}")
    average_weapon_damage_per_type = calculate_average_weapon_damage_per_type("JSON-and-old-cache-method/weapon-data.json")
    calculate_difference_awdpt(average_weapon_damage_per_type)

    print(f"{'#'*91}\n{'#'*91}\n{'#'*91}\n")



    print(f"{'#'*30} Num Artifacts per Max Quality {'#'*30}")

    calculate_num_artifacts_per_quality("JSON-and-old-cache-method/artifact-data.json")

    function_calls = [
        (calculate_average_weapon_damage_per_rarity, ("JSON-and-old-cache-method/weapon-data.json",)),
        (calculate_difference_awdpr, (average_weapon_damage_per_rarity,)),
        (calculate_average_weapon_damage_per_type, ("JSON-and-old-cache-method/weapon-data.json",)),
        (calculate_difference_awdpt, (average_weapon_damage_per_type,)),
        (calculate_num_artifacts_per_quality, ("JSON-and-old-cache-method/artifact-data.json",))
    ]
    with open("calculations.txt", "w") as file:
        for func, args in function_calls:
            result = func(*args)  # Call the function with the arguments
            file.write(f"{func.__name__}\n{'-'*20}\n({', '.join(map(str, args))}) = {result}\n\n\n")

main()