
# eva was here

import sqlite3
import json
import os
import re

def read_data_from_file(filename):
    """
    Reads data from a file with the given filename.

    Parameters
    -----------------------
    filename: str
        The name of the file to read.

    Returns
    -----------------------
    dict:
        Parsed JSON data from the file.
    """
    full_path = os.path.join(os.path.dirname(__file__), filename)
    with open(full_path, "r") as f:
        json_data = json.load(f)
    return json_data

def set_up_database(db_name):
    """
    Sets up a SQLite database connection and cursor.

    Parameters
    -----------------------
    db_name: str
        The name of the SQLite database.

    Returns
    -----------------------
    Tuple (Cursor, Connection):
        A tuple containing the database cursor and connection objects.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_weapons_table(cur, conn):
    """
    Sets up the Weapons table in the database using the provided Weapon data.

    Parameters
    -----------------------
    data: list
        List of Weapon data in JSON format.

    cur: Cursor
        The database cursor object.

    conn: Connection
        The database connection object.

    Returns
    -----------------------
    None

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
    Sets up the Characters table in the database using the provided Character data.

    Parameters
    -----------------------
    data: list
        List of Character data in JSON format.

    cur: Cursor
        The database cursor object.

    conn: Connection
        The database connection object.

    Returns
    -----------------------
    None

    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Characters (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            rarity TEXT NOT NULL,
            weapon TEXT NOT NULL,
            vision TEXT NOT NULL
        )
        """
    )
    conn.commit()


def set_up_banners_table(cur, conn):
    """
    Sets up the Banners table in the database using the provided Banner data.

    Parameters
    -----------------------
    data: list
        List of Banner data in JSON format.

    cur: Cursor
        The database cursor object.

    conn: Connection
        The database connection object.

    Returns
    -----------------------
    None

    Notes
    -----------------------
    Only allowed the number value for rarity to be put into the table for simiplifcation reasons
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Banners (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            version TEXT,
            start_date TEXT NOT NULL,
            end_date TEXT,
            featured_character TEXT,
            first_three_star TEXT,
            second_three_star TEXT,
            third_three_star TEXT
        )
        """
    )
    conn.commit()

def set_up_artifacts_table(cur, conn):
    """
    Sets up the Artifacts table in the database.

    Parameters
    -----------------------
    cur: Cursor
        The database cursor object.

    conn: Connection
        The database connection object.

    Returns
    -----------------------
    None
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Artifacts (
            id INTEGER PRIMARY KEY,
            set_name TEXT NOT NULL,
            piece_1 TEXT,
            piece_2 TEXT,
            piece_3 TEXT,
            piece_4 TEXT,
            piece_5 TEXT,
            set_bonus_2 TEXT,
            set_bonus_4 TEXT
        )
        """
    )
    conn.commit()


def insert_weapons_data(cur, conn, weapon_data):
    """
    Inserts the weapons data into the sqlite file 
    
    Parameters
    -----------------------
    weapon_data: list
        List of weapon data in JSON format.

    cur: Cursor
        The database cursor object.

    conn: Connection
        The database connection object.

    Returns
    -----------------------
    None

    Notes 
    -----------------------
    Limiting: The logic here is that it is able to count the existing rows and continues to add to it (applies to rest of the functions too)

    """
    cur.execute("SELECT COUNT(*) FROM Weapons")
    start_index = cur.fetchone()[0]

    for weapon in weapon_data[start_index:start_index + 25]:
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
    Inserts the character data into the sqlite file 
    
    Parameters
    -----------------------
    character_data: list
        List of character data in JSON format.

    cur: Cursor
        The database cursor object.

    conn: Connection
        The database connection object.

    Returns
    -----------------------
    None
    """

    cur.execute("SELECT COUNT(*) FROM Characters")
    start_index = cur.fetchone()[0]


    for character in character_data[start_index:start_index + 25]:
        rarity = re.match(r"(\d+)", character["rarity"])
        rarity = int(rarity.group(1)) if rarity else None

        cur.execute(
            """
            INSERT OR REPLACE INTO Characters (
                id, name, rarity, weapon, vision
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                character["id"],
                character["name"],
                rarity,
                character["weapon"],
                character["vision"]
            )
        )
    conn.commit()


def insert_banners_data(cur, conn, banner_data):
    """
    Inserts the banner data into the sqlite file 
    
    Parameters
    -----------------------
    banner_data: list
        List of banner data in JSON format.

    cur: Cursor
        The database cursor object.

    conn: Connection
        The database connection object.

    Returns
    -----------------------
    None
    """
    cur.execute("SELECT COUNT(*) FROM Banners")
    start_index = cur.fetchone()[0]

    
    for banner in banner_data[start_index:start_index + 25]:
        end_date = None if banner.get('type') == "Permanent" else banner.get('end', 'Unknown End Date')
        featured = banner.get('featured', [])
        featured_character = featured[0]['name'] if len(featured) > 0 else None
        first_three_star = featured[1]['name'] if len(featured) > 1 else None
        second_three_star = featured[2]['name'] if len(featured) > 2 else None
        third_three_star = featured[3]['name'] if len(featured) > 3 else None

        cur.execute(
            '''
            INSERT OR REPLACE INTO Banners (
                name, type, version, start_date, end_date, 
                featured_character, first_three_star, second_three_star, third_three_star
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                banner['name'], banner['type'], banner['version'], banner['start'], end_date,
                featured_character, first_three_star, second_three_star, third_three_star
            )
        )
    conn.commit()

def insert_artifacts_data(cur, conn, data):
    """
    Inserts artifact data into the Artifacts table.

    Parameters
    -----------------------
    cur: Cursor
        The database cursor object.

    conn: Connection
        The database connection object.

    data: list
        List of artifact data in JSON format.

    Returns
    -----------------------
    None
    """
    # Organize artifacts by set name
    sets = {}
    for artifact in data:
        set_name = artifact["artifactSetName"]
        if set_name not in sets:
            sets[set_name] = {
                "pieces": [],
                "set_bonus_2": None,
                "set_bonus_4": None
            }
        
        # Add artifact piece
        sets[set_name]["pieces"].append(artifact["name"])
        
        # Add set bonuses if available
        for bonus in artifact.get("setBonuses", []):
            if bonus["pieces"] == 2:
                sets[set_name]["set_bonus_2"] = bonus["bonus"]
            elif bonus["pieces"] == 4:
                sets[set_name]["set_bonus_4"] = bonus["bonus"]

    # Insert data into the database
    for set_name, info in sets.items():
        pieces = info["pieces"]
        cur.execute(
            """
            INSERT INTO Artifacts (set_name, piece_1, piece_2, piece_3, piece_4, piece_5, set_bonus_2, set_bonus_4)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                set_name,
                pieces[0] if len(pieces) > 0 else None,
                pieces[1] if len(pieces) > 1 else None,
                pieces[2] if len(pieces) > 2 else None,
                pieces[3] if len(pieces) > 3 else None,
                pieces[4] if len(pieces) > 4 else None,
                info["set_bonus_2"],
                info["set_bonus_4"]
            )
        )
    conn.commit()

def main():
    """
    Main function
    -----------------------
    Reads JSON Data

    Sets up the data base called genshin_impact.db

    Sets up the tables (weapons,characters,banners)

    Inserts the data into the tables

    Closes connection
    -----------------------

    """
    
    # Read the JSON data
    weapon_data = read_data_from_file('weapon-data.json')
    character_data = read_data_from_file('character-data.json')
    banner_data = read_data_from_file('banner-data.json')
    artifact_data = read_data_from_file('artifact-data.json')

    # Set up the database
    cur, conn = set_up_database('genshin_impact.db')

    # Set up the tables
    set_up_weapons_table(cur, conn)
    set_up_characters_table(cur, conn)
    set_up_banners_table(cur, conn)
    set_up_artifacts_table (cur,conn)

    # Insert the data
    insert_weapons_data(cur, conn, weapon_data)
    insert_characters_data(cur, conn, character_data)
    insert_banners_data(cur, conn, banner_data)
    insert_artifacts_data(cur,conn,artifact_data)

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
