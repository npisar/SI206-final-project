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
    fig = plt.figure(1, figsize=(12,6))
    bx1 = fig.add_subplot(121)
    bars = fig.add_subplot(122)
    colors = ['#ac92eb','#4fc1e8','#a0d568','#ffce54','#ed5564']

    # format and populate the boxplot
    nested_lst = [one_star, two_star, three_star, four_star, five_star]
    bx1.boxplot(nested_lst, patch_artist=True)
    bx1.set_title("Weapon Damage by Rarity")
    bx1.set_xlabel("Rarity")
    bx1.set_ylabel("Base Damage")
    bx1.set_xticks([1, 2, 3, 4, 5])

    # format and populate the bar chart
    rarities = ['1 Star','2 Star','3 Star','4 Star','5 Star']
    counts  = [len(one_star), len(two_star), len(three_star), len(four_star), len(five_star)]
    bars.barh(rarities, counts, color=colors)
    bars.set_title("Number of Weapons by Rarity")
    bars.ticklabel_format(axis='x', style='plain')
    bars.set_xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    bars.set_xlabel("Number of Weapons")
    bars.set_ylabel("Rarity")

    # display and save the visualizations as a png file
    plt.show()
    plt.savefig('rarity_vs_dmg_and_frequency.png', dpi=300, bbox_inches='tight')



def get_char_stats(cur):
    '''
    ARGUMENTS
        cur: The cursor object used to pull the weapon info from the database

    RETURNS:
        char_d: A nested dictionary containing weapon info in the following format:
        {"Character Name"(str): {'Rarity': "Character Rarity"(int), 'Weapon': "Weapon Type"(str), 'Vision': "Character Vision"(str)}}
    '''
    # pull the characters and their corresponding stats from the database
    cur.execute('''SELECT name, rarity, weapon_type_id, vision_id FROM Characters ''')

    # create a nested dictionary with character names as outer keys, 
    # rarity, weapon, and vision as inner keys, and the corresponding information as inner values
    chars_d = {}
    for character in cur:
        name = character[0]
        rarity = character[1]
        weapon = character[2]
        vision = character[3]
        nested_d = {}
        nested_d['Rarity'] = rarity
        nested_d['Weapon'] = weapon
        nested_d['Vision'] = vision
        if name not in chars_d:
            chars_d[name] = nested_d
    return chars_d
    


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
    fig1 = plt.figure(1, figsize=(30,10))
    bar1 = fig1.add_subplot(131)
    bar2 = fig1.add_subplot(132)
    bar3 = fig1.add_subplot(133)

    # format and populate the bar charts
    bar1.bar(d['Pyro'].keys(), d['Pyro'].values(), color='#FFD6A5')
    bar1.set_title("Weapon Choice for Pyros")
    bar1.ticklabel_format(axis='y', style='plain')
    bar1.set_yticks([1, 2, 3, 4, 5])
    bar1.set_xlabel("Weapon")
    bar1.set_ylabel("Frequency") 

    bar2.bar(d['Hydro'].keys(), d['Hydro'].values(), color='#aoc4ff')
    bar2.set_title("Weapon Choice for Hydros")
    bar2.ticklabel_format(axis='y', style='plain')
    bar2.set_yticks([1, 2, 3, 4, 5])
    bar2.set_xlabel("Weapon")
    bar2.set_ylabel("Frequency") 

    bar3.bar(d['Electro'].keys(), d['Electro'].values(), color='#BD2bFF')
    bar3.set_title("Weapon Choice for Electros")
    bar3.ticklabel_format(axis='y', style='plain')
    bar3.set_yticks([1, 2, 3, 4, 5])
    bar3.set_xlabel("Weapon")
    bar3.set_ylabel("Frequency")

    # display and save the visualizations as a png file
    plt.show()
    plt.savefig('weapon_by_vision1.png', dpi=300, bbox_inches='tight')

    # Create the second figure and subplots: three bar charts
    fig2 = plt.figure(1, figsize=(30,10))
    bar4 = fig2.add_subplot(131)
    bar5 = fig2.add_subplot(132)
    bar6 = fig2.add_subplot(133)

    # format and populate the bar charts
    bar4.bar(d['Cryo'].keys(), d['Cryo'].values(), color='#9bf6ff')
    bar4.set_title("Weapon Choice for Cryos")
    bar4.ticklabel_format(axis='y', style='plain')
    bar4.set_yticks([1, 2, 3, 4, 5])
    bar4.set_xlabel("Weapon")
    bar4.set_ylabel("Frequency") 

    bar5.bar(d['Geo'].keys(), d['Geo'].values(), color='#ffADAD')
    bar5.set_title("Weapon Choice for Geos")
    bar5.ticklabel_format(axis='y', style='plain')
    bar5.set_yticks([1, 2, 3, 4, 5])
    bar5.set_xlabel("Weapon")
    bar5.set_ylabel("Frequency") 

    bar6.bar(d['Anemo'].keys(), d['Anemo'].values(), color='#caffbf')
    bar6.set_title("Weapon Choice for Anemos")
    bar6.ticklabel_format(axis='y', style='plain')
    bar6.set_yticks([1, 2, 3, 4, 5])
    bar6.set_xlabel("Weapon")
    bar6.set_ylabel("Frequency")

    # display and save the visualizations as a png file
    plt.show()
    plt.savefig('weapon_by_vision2.png', dpi=300, bbox_inches='tight')



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
    colors = ['#FFD6A5','#aoc4ff','#caffbf','#BD2bFF','#9bf6ff', '#ffADAD', '#caffbf']
    plt.pie(counts_d.values(), labels=counts_d.keys(), autopct='%1.1f%%', colors=colors)
    plt.title('Character Vision Distribution')

    # display and save the visualizations as a png file
    plt.show()
    plt.savefig('chars_by_vision.png', dpi=300, bbox_inches='tight')



def main():
    # create the connection and cursor
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'genshin_impact_data.db')
    cur = conn.cursor()

    # call the functions to gather the needed information from the database 
    weapons_info = get_weapon_stats(cur)
    character_info = get_char_stats(cur)

    # call the functions to create the visualizations
    box_rarity_versus_dmg(weapons_info)
    char_vision_vs_weapon(character_info)
    chars_by_vision(character_info)


main()