import matplotlib.pyplot as plt
import sqlite3
import os

def get_weapon_stats(cur):
    '''
    ARGUMENTS
        cur: The cursor object used to pull the weapon info from the database

    RETURNS:
        weapons_d: A nested dictionary containing weapon info in the following format:
        {"Weapon Name"(str): {'Type': "Weapon Type"(str), 'Rarity': "Weapon Rarity"(int), 'Damage': "Base Weapon Damage"(int)}}
    '''
    cur.execute('''SELECT id, weapon_type_id, rarity, base_attack FROM Weapons ''')

    weapons_d = {}
    for weapon in cur:
        name = weapon[0]
        type = weapon[1]
        rarity = weapon[2]
        dmg = weapon[3]
        nested_d = {}
        nested_d['Type'] = type
        nested_d['Rarity'] = rarity
        nested_d['Damage'] = dmg
        if name not in weapons_d:
            weapons_d[name] = nested_d

    return weapons_d



def get_char_stats(cur):
    '''
    ARGUMENTS
        cur: The cursor object used to pull the weapon info from the database

    RETURNS:
        char_d: A nested dictionary containing weapon info in the following format:
        {"Character Name"(str): {'Rarity': "Character Rarity"(int), 'Weapon': "Weapon Type"(str), 'Vision': "Character Vision"(str)}}
    '''
    # pull the characters and their corresponding stats from the database
    cur.execute(
        '''
        SELECT Characters.name, Characters.rarity, CharacterVisions.vision, WeaponTypes.weapon_type
        FROM Characters JOIN CharacterVisions JOIN WeaponTypes
        ON Characters.weapon_id = WeaponTypes.id and Characters.vision_id = CharacterVisions.id
        '''
        )

    # create a nested dictionary with character names as outer keys, 
    # rarity, weapon, and vision as inner keys, and the corresponding information as inner values
    rows = cur.fetchall()
    chars_d = {}
    for row in rows:
        name = row[0]
        rarity = row[1]
        vision = row[2]
        weapon = row[3]
        nested_d = {}
        nested_d['Rarity'] = rarity
        nested_d['Weapon'] = weapon
        nested_d['Vision'] = vision
        if name not in chars_d:
            chars_d[name] = nested_d
            
    return chars_d



def get_artifact_stats(cur):
    '''
    ARGUMENTS
        cur: The cursor object used to pull the weapon info from the database

    RETURNS:
        artifact_d: A  dictionary containing artifact info in the following format:
        {'Artifact Name': "Name"(str), 'Max Set Quality': Quality from 1-5(int)}
    '''
    cur.execute('''SELECT name, maxSetQuality FROM Artifacts ''')

    matches = cur.fetchall()
    artifact_d = dict(matches)
    return artifact_d



def box_rarity_versus_dmg(weapons_d):
    '''
    ARGUMENTS
        weapons_d: The dictionary with each weapon and its statistics

    RETURNS:
        None
    '''
    # Sort the weapon damage amounts by their rating
    one_star = []
    two_star = []
    three_star = []
    four_star = []
    five_star = []
    for weapon in weapons_d.values(): 
        if weapon['Rarity'] == 1:
            one_star.append(weapon['Damage'])
        elif weapon['Rarity'] == 2:
            two_star.append(weapon['Damage'])
        elif weapon['Rarity'] == 3:
            three_star.append(weapon['Damage'])
        elif weapon['Rarity'] == 4:
            four_star.append(weapon['Damage'])
        else:
            five_star.append(weapon['Damage'])
    
    # Create the figure and subplots: one box plot and one horizontal bar chart
    fig = plt.figure(1, figsize=(8,6))
    bx1 = fig.add_subplot(121)
    bars = fig.add_subplot(122)
    colors = ['#ac92eb','#4fc1e8','#a0d568','#ffce54','#ed5564']

    # format and populate the boxplot
    nested_lst = [one_star, two_star, three_star, four_star, five_star]
    bx1.boxplot(nested_lst, patch_artist=True)
    bx1.set_title("Weapon Damage by Rarity")
    bx1.set_xlabel("Rarity (Stars)")
    bx1.set_ylabel("Base Damage")
    bx1.set_xticks([1, 2, 3, 4, 5])

    # format and populate the bar chart
    rarities = [1, 2, 3, 4, 5]
    counts  = [len(one_star), len(two_star), len(three_star), len(four_star), len(five_star)]
    bars.barh(rarities, counts, color=colors)
    bars.set_title("Number of Weapons by Rarity")
    bars.ticklabel_format(axis='x', style='plain')
    bars.set_xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    bars.set_xlabel("Number of Weapons")
    bars.set_ylabel("Rarity (Stars)")

    # display and save the visualizations as a png file
    plt.savefig('graphs/rarity_vs_dmg_and_frequency.png', dpi=300, bbox_inches='tight')
    plt.show()
    


def char_vision_vs_weapon(chars_d):
    '''
    ARGUMENTS
        weapons_d: The dictionary with each weapon and its statistics

    RETURNS:
        None
    '''
    # create a nested dictionary with each vision as the outer keys, each weapon type
    # as inner keys, and the number of users for that weapon/vision combo as inner values 
    d = {}
    for character in chars_d.values():
        vision = character['Vision']
        weapon = character['Weapon']
        if vision not in d:
            d[vision] = {}
        d[vision][weapon] = d[vision].get(weapon, 0) + 1

    # Create the first figure and subplots: three bar charts
    fig1 = plt.figure(1, figsize=(16,8))
    bar1 = fig1.add_subplot(131)
    bar2 = fig1.add_subplot(132)
    bar3 = fig1.add_subplot(133)

    # format and populate the bar charts
    bar1.bar(d['Pyro'].keys(), d['Pyro'].values(), color='#FFD6A5')
    bar1.set_title("Weapon Choice for Pyros", fontsize=10)
    bar1.ticklabel_format(axis='y', style='plain')
    bar1.set_yticks([1, 2, 3, 4, 5])
    bar1.set_xlabel("Weapon")
    bar1.set_ylabel("Frequency")
    bar1.tick_params(axis="x", labelrotation=35, labelsize=8)

    bar2.bar(d['Hydro'].keys(), d['Hydro'].values(), color='#A0C4FF')
    bar2.set_title("Weapon Choice for Hydros", fontsize=10)
    bar2.ticklabel_format(axis='y', style='plain')
    bar2.set_yticks([1, 2, 3, 4, 5])
    bar2.set_xlabel("Weapon")
    bar2.set_ylabel("Frequency") 
    bar2.tick_params(axis="x", labelrotation=35, labelsize=8)

    bar3.bar(d['Electro'].keys(), d['Electro'].values(), color='#BD2BFF')
    bar3.set_title("Weapon Choice for Electros", fontsize=10)
    bar3.ticklabel_format(axis='y', style='plain')
    bar3.set_yticks([1, 2, 3, 4, 5])
    bar3.set_xlabel("Weapon")
    bar3.set_ylabel("Frequency")
    bar3.tick_params(axis="x", labelrotation=35, labelsize=8)

    # display and save the visualizations as a png file
    plt.savefig('graphs/weapon_by_vision1.png', dpi=300, bbox_inches='tight')
    plt.show()

    # Create the second figure and subplots: three bar charts
    fig2 = plt.figure(1, figsize=(16,8))
    bar4 = fig2.add_subplot(131)
    bar5 = fig2.add_subplot(132)
    bar6 = fig2.add_subplot(133)

    # format and populate the bar charts
    bar4.bar(d['Cryo'].keys(), d['Cryo'].values(), color='#9BF6FF')
    bar4.set_title("Weapon Choice for Cryos", fontsize=10)
    bar4.ticklabel_format(axis='y', style='plain')
    bar4.set_yticks([1, 2, 3, 4, 5])
    bar4.set_xlabel("Weapon")
    bar4.set_ylabel("Frequency") 
    bar4.tick_params(axis="x", labelrotation=35, labelsize=8)

    bar5.bar(d['Geo'].keys(), d['Geo'].values(), color='#FFADAD')
    bar5.set_title("Weapon Choice for Geos", fontsize=10)
    bar5.ticklabel_format(axis='y', style='plain')
    bar5.set_yticks([1, 2, 3, 4, 5])
    bar5.set_xlabel("Weapon")
    bar5.set_ylabel("Frequency")
    bar5.tick_params(axis="x", labelrotation=35, labelsize=8)

    bar6.bar(d['Anemo'].keys(), d['Anemo'].values(), color='#CAFFBF')
    bar6.set_title("Weapon Choice for Anemos", fontsize=10)
    bar6.ticklabel_format(axis='y', style='plain')
    bar6.set_yticks([1, 2, 3, 4, 5])
    bar6.set_xlabel("Weapon")
    bar6.set_ylabel("Frequency")
    bar6.tick_params(axis="x", labelrotation=35, labelsize=8)

    # display and save the visualizations as a png file
    plt.savefig('graphs/weapon_by_vision2.png', dpi=300, bbox_inches='tight')
    plt.show()



def chars_by_vision(chars_d):
    '''
    ARGUMENTS
        weapons_d: The dictionary with each weapon and its statistics

    RETURNS:
        None
    '''
    # create a dictionary with each character vision as a key and their respective counts as values
    counts_d = {}
    for character in chars_d.values():
        vision = character['Vision']
        counts_d[vision] = counts_d.get(vision, 0) + 1

     # Create and populate the graph: a pie chart
    colors = ['#FFD6A5','#A0C4FF','#CAFFBF','#BD2BFF','#9BF6FF', '#FFADAD', '#CAFFBF']
    plt.pie(counts_d.values(), labels=counts_d.keys(), autopct='%1.1f%%', colors=colors)
    plt.title('Character Vision Distribution')

    # display and save the visualizations as a png file
    plt.savefig('graphs/chars_by_vision.png', dpi=300, bbox_inches='tight')
    plt.show()



def artifact_qual_dist(artifact_d):
    '''
    ARGUMENTS
        artifact_d: The dictionary with each artifact and its maximum set quality
    
    RETURNS:
        None
    '''
    # create a dictionary with each quality(1-5 stars) as the key and their respective counts as values
    rarity_counts = {}
    for artifact in artifact_d.values():
        rating = (str(artifact)+' Star')
        rarity_counts[rating] = rarity_counts.get(rating, 0) + 1
    
    # Create and populate the graph: a pie chart
    colors = ['#aca2e0','#f4e8c1','#a0c1b9','#70a0af']
    plt.pie(rarity_counts.values(), labels=rarity_counts.keys(), autopct='%1.1f%%', colors=colors)
    plt.title('Maximum Artifact Set Quality Distribution')

    # display and save the visualizations as a png file
    plt.savefig('graphs/artifacts_by_qual.png', dpi=300, bbox_inches='tight')
    plt.show()



def main():
    # create the connection and cursor
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "..")) 
    db_path = os.path.join(root_dir, 'genshin_impact_data.db')
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # call the functions to gather the needed information from the database 
    weapons_info = get_weapon_stats(cur)
    character_info = get_char_stats(cur)
    artifact_info = get_artifact_stats(cur)

    # call the functions to create the visualizations
    box_rarity_versus_dmg(weapons_info)
    char_vision_vs_weapon(character_info)
    chars_by_vision(character_info)
    artifact_qual_dist(artifact_info)

    # close the connection
    conn.close()

if __name__ == "__main__":
    main()