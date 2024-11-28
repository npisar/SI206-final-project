
# eva was here


import sqlite3
import json
import os

def read_data_from_file(filename):
    """
    Reads data from a file with the given filename.
    """
    full_path = os.path.join(os.path.dirname(__file__), filename)
    with open(full_path, "r") as f:
        json_data = json.load(f)
    return json_data

def set_up_database(db_name):
    """
    Sets up a SQLite database connection and cursor.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_weapons_table(cur, conn):
    """
    Creates the Weapons table.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Weapons (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            rarity INTEGER NOT NULL,
            base_attack INTEGER NOT NULL,
            sub_stat TEXT,
            passive_name TEXT,
            passive_desc TEXT,
            location TEXT,
            ascension_material TEXT
        )
        """
    )
    conn.commit()

def set_up_characters_table(cur, conn):
    """
    Creates the Characters table.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Characters (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            title TEXT,
            vision TEXT NOT NULL,
            weapon TEXT NOT NULL,
            nation TEXT,
            affiliation TEXT,
            rarity INTEGER NOT NULL,
            constellation TEXT,
            birthday TEXT,
            utility_passive TEXT,
            normal_talent_name TEXT,
            skill_talent_name TEXT,
            burst_talent_name TEXT
        )
        """
    )
    conn.commit()

def set_up_banners_table(cur, conn):
    """
    Creates the Banners and FeaturedCharacters tables.
    """
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Banners (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT,
        version TEXT,
        start_date TEXT,
        end_date TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS FeaturedCharacters (
        id INTEGER PRIMARY KEY,
        banner_id INTEGER,
        role TEXT,
        name TEXT NOT NULL,
        character_id TEXT NOT NULL,
        rarity INTEGER,
        FOREIGN KEY (banner_id) REFERENCES Banners(id)
    )
    ''')

    conn.commit()

def insert_weapons_data(cur, conn, weapon_data):
    """
    Inserts weapon data into the Weapons table.
    """
    for weapon in weapon_data:
        cur.execute(
            """
            INSERT OR REPLACE INTO Weapons (
                id, name, type, rarity, base_attack, sub_stat, 
                passive_name, passive_desc, location, ascension_material
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                weapon["id"], weapon["name"], weapon["type"], weapon["rarity"], 
                weapon["baseAttack"], weapon.get("subStat"), weapon.get("passiveName"),
                weapon.get("passiveDesc"), weapon["location"], weapon["ascensionMaterial"]
            )
        )
    conn.commit()

def insert_characters_data(cur, conn, character_data):
    """
    Inserts character data into the Characters table.
    """
    for character in character_data:
        normal_talent = next(
            (talent["name"] for talent in character["skillTalents"] if talent["unlock"] == "Normal Attack"), None
        )
        skill_talent = next(
            (talent["name"] for talent in character["skillTalents"] if talent["unlock"] == "Elemental Skill"), None
        )
        burst_talent = next(
            (talent["name"] for talent in character["skillTalents"] if talent["unlock"] == "Elemental Burst"), None
        )

        utility_passive = next(
            (passive["name"] for passive in character["passiveTalents"] if passive["unlock"] == "Unlocked Automatically"), None
        )

        cur.execute(
            """
            INSERT OR REPLACE INTO Characters (
                id, name, title, vision, weapon, nation, affiliation, 
                rarity, constellation, birthday, utility_passive, 
                normal_talent_name, skill_talent_name, burst_talent_name
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                character["id"], character["name"], character.get("title"), 
                character["vision"], character["weapon"], character.get("nation", "Unknown"), 
                character.get("affiliation", "Unknown"), character["rarity"], 
                character["constellation"], character.get("birthday", "Unknown"), 
                utility_passive, normal_talent, skill_talent, burst_talent
            )
        )
    conn.commit()

def insert_banners_data(cur, conn, banner_data):
    """
    Inserts banner data into the Banners and FeaturedCharacters tables.
    """
    for banner in banner_data:
        cur.execute('''
        INSERT INTO Banners (name, type, version, start_date, end_date)
        VALUES (?, ?, ?, ?, ?)
        ''', (banner['name'], banner['type'], banner['version'], banner['start'], banner['end']))
        
        banner_id = cur.lastrowid  # Get the last inserted banner id

        featured = banner.get('featured', [])
        
        for i, character in enumerate(featured):
            role = "Featured Character" if i == 0 else f"Three Star {i}"
            cur.execute('''
            INSERT INTO FeaturedCharacters (banner_id, role, name, character_id, rarity)
            VALUES (?, ?, ?, ?, ?)
            ''', (banner_id, role, character['name'], character['id'], character.get('rarity', 4)))
    
    conn.commit()

def main():
    # Read the JSON data
    weapon_data = read_data_from_file('weapons.json')
    character_data = read_data_from_file('characters.json')
    banner_data = read_data_from_file('banners.json')

    # Set up the database
    cur, conn = set_up_database('genshin_impact.db')

    # Set up the tables
    set_up_weapons_table(cur, conn)
    set_up_characters_table(cur, conn)
    set_up_banners_table(cur, conn)

    # Insert the data
    insert_weapons_data(cur, conn, weapon_data)
    insert_characters_data(cur, conn, character_data)
    insert_banners_data(cur, conn, banner_data)

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
