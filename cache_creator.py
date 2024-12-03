
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
    """
    batch_size = 25
    for i in range(0, len(weapon_data), batch_size):
        batch = weapon_data[i:i + batch_size]
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
    batch_size = 25
    for i in range(0, len(character_data), batch_size):
        batch = character_data[i:i + batch_size]
        for character in character_data:
            # Extracting numeric part of the rarity (e.g., "4_star" becomes "4")
            rarity = re.match(r"(\d+)", character["rarity"])
            rarity = int(rarity.group(1)) if rarity else None  # Default to None if no number found

            # Insert character data into the database
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

        # Commit changes to the database
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
    batch_size = 25
    for i in range(0, len(banner_data), batch_size):
        batch = banner_data[i:i + batch_size]
        for banner in banner_data:
            # Determine end_date based on type
            end_date = None if banner.get('type') == "Permanent" else banner.get('end', 'Unknown End Date')

            # Extract character categories
            featured = banner.get('featured', [])
            featured_character = featured[0]['name'] if len(featured) > 0 else None
            first_three_star = featured[1]['name'] if len(featured) > 1 else None
            second_three_star = featured[2]['name'] if len(featured) > 2 else None
            third_three_star = featured[3]['name'] if len(featured) > 3 else None

            # Debugging print statements
            #print("Inserting Banner:", banner['name'])
            #print("Five Star:", featured_character)
            #print("1st Three Star:", first_three_star)
            #print("2nd Three Star:", second_three_star)
            #print("3rd Three Star:", third_three_star)

            # Insert or update the banner
            cur.execute('''
            INSERT OR REPLACE INTO Banners (name, type, version, start_date, end_date, featured_character, first_three_star, second_three_star, third_three_star)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (banner['name'], banner['type'], banner['version'], banner['start'], end_date,
                featured_character, first_three_star, second_three_star, third_three_star))

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
