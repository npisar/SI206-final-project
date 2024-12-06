#eva was here

import sqlite3
import requests
from bs4 import BeautifulSoup
import re

#data base created
def set_up_database(db_name):
    """
    Sets up a SQLite database connection and cursor.

    Parameters:
    -----------------------
    db_name: str
        The name of the SQLite database.

    Returns:
    -----------------------
    Tuple (Cursor, Connection):
        A tuple containing the database cursor and connection objects.
    """
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    return cur, conn

##########################--WEAPONS--#################################

#api call to establish connection to weapons database
def get_weapon_names(weapon_url):
    """
    Fetches all weapon names from the API.

    Parameters:
    --------------------
    weapon_url: str
        The base URL for the API.

    Returns:
    --------------------
    list[str]:
        A list of weapon names retrieved from the API.
    """
    response = requests.get(f"{weapon_url}weapons/")
    if response.status_code != 200:
        print(f"Error fetching weapon names: {response.status_code}")
        return []
    
    weapon_names = response.json()
    return weapon_names

#iterator that collects all of the weapon information
def weapon_list(weapon_url, weapon_names, cur, conn):
    """
    Fetches detailed data for each weapon and stores it in the SQLite database.

    Parameters:
    --------------------
    weapon_url: str
        The base URL for the API.

    weapon_names: list[str]
        A list of weapon names to fetch details for.

    cur: sqlite3.Cursor
        The SQLite database cursor.

    conn: sqlite3.Connection
        The SQLite database connection.
    """
    #get the weapon names and put them through the api to get all weapon information
    for weapon_name in weapon_names:
        response = requests.get(f"{weapon_url}weapons/{weapon_name}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for weapon: {weapon_name}, Status: {response.status_code}")
            continue

        weapon_data = response.json()
        insert_weapon_data(cur, conn, weapon_data)

#create the tables we will use for weapon data
def set_up_weapons_table(cur, conn):
    """
    Sets up the Weapons table in the database with only type, rarity, and base attack.

    cur: sqlite3.Cursor
        The database cursor object.

    conn: sqlite3.Connection
        The database connection object.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Weapons (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            rarity INTEGER NOT NULL,
            base_attack INTEGER NOT NULL
        )
        """
    )
    conn.commit()

#applies the weapon data into the table we made 
def insert_weapon_data(cur, conn, weapon_data):
    """
    Inserts the detailed weapon data into the database with only type, rarity, and base attack.

    Parameters:
    --------------------
    cur: sqlite3.Cursor
        The SQLite database cursor.

    conn: sqlite3.Connection
        The SQLite database connection.

    weapon_data: dict
        The detailed weapon data to insert into the database.
    """
    cur.execute(
        """
        INSERT OR IGNORE INTO Weapons 
        (id, type, rarity, base_attack)
        VALUES (?, ?, ?, ?)
        """,
        (
            weapon_data['id'],
            weapon_data['type'],
            weapon_data['rarity'],
            weapon_data['baseAttack']
        )
    )
    conn.commit()

def create_weapon_types_table(cur, conn):
    """
    Creates a table for weapon types with unique numeric IDs.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS WeaponTypes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT UNIQUE NOT NULL
        )
        """
    )
    conn.commit()

def get_weapon_type_id(cur, conn, weapon_type):
    """
    Inserts a weapon type if it doesn't exist and returns its ID.
    """
    cur.execute(
        """
        INSERT OR IGNORE INTO WeaponTypes (type)
        VALUES (?)
        """,
        (weapon_type,)
    )
    conn.commit()

    # Retrieve the ID of the weapon type
    cur.execute(
        """
        SELECT id FROM WeaponTypes
        WHERE type = ?
        """,
        (weapon_type,)
    )
    return cur.fetchone()[0]


##########################--CHARACTERS--#################################

# API call to establish connection to the character database
def get_character_ids(character_url):
    """
    Fetches all character IDs and names from the API.

    Parameters:
    --------------------
    character_url: str
        The base URL for the API.

    Returns:
    --------------------
    list[dict]:
        A list of dictionaries containing character IDs and names.
    """
    all_characters = []

    # Fetch all characters from the API (pagination can be added if needed)
    resp = requests.get(f"{character_url}characters/")
    if resp.status_code != 200:
        print(f"Failed to fetch data: {resp.status_code}")
        return []

    data = resp.json()
    characters = data.get('results', [])

    # Collect character IDs and names
    all_characters = [{'id': char['id'], 'name': char['name']} for char in characters]
    return all_characters

# Table for storing character IDs and names
def set_up_character_table(cur, conn):
    """
    Creates the Characters table with fields for id and name.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Characters (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        """
    )
    conn.commit()

# Table for storing character IDs and their associated weapons
def set_up_character_weapon_table(cur, conn):
    """
    Creates a CharactersWeapons table to store character IDs and weapon types.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS CharactersWeapons (
            id INTEGER PRIMARY KEY,  -- Character ID
            weapon TEXT NOT NULL     -- Weapon type used by the character
        )
        """
    )
    conn.commit()

# Insert characters into SQLite database
def character_list(character_url, cur, conn):
    """
    Fetches and inserts detailed character data (id, name) for each character ID into the Characters table.
    """
    for char_id in range(1, 52):  # Loop through character IDs 1 to 51
        response = requests.get(f"{character_url}characters/{char_id}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for character ID {char_id}, Status: {response.status_code}")
            continue

        character_data = response.json().get('result', {})  # Extract the 'result' field

        char_id = character_data.get('id')
        char_name = character_data.get('name')

        if not char_id or not char_name:
            print(f"Invalid data for character ID {char_id}: {character_data}")
            continue

        # Insert the data into the Characters table
        try:
            cur.execute("""
                INSERT OR IGNORE INTO Characters (id, name)
                VALUES (?, ?)
            """, (char_id, char_name))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error for character ID {char_id}: {e}")

def character_weapon_list_weapons(character_url, cur, conn):
    """
    Fetches and inserts character weapon data (id, weapon) for each character ID into the CharactersWeapons table.
    """
    for char_id in range(1, 52):  # Loop through character IDs 1 to 51
        response = requests.get(f"{character_url}characters/{char_id}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for character ID {char_id}, Status: {response.status_code}")
            continue

        character_data = response.json().get('result', {})  # Extract the 'result' field

        char_id = character_data.get('id')
        char_weapon = character_data.get('weapon')

        if not char_id or not char_weapon:
            print(f"Invalid data for character ID {char_id}: {character_data}")
            continue

        # Insert the data into the CharactersWeapons table
        try:
            cur.execute("""
                INSERT OR IGNORE INTO CharactersWeapons (id, weapon)
                VALUES (?, ?)
            """, (char_id, char_weapon))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error for character ID {char_id}: {e}")

def create_characters_table(cur, conn):
    """
    Creates the Characters table with a reference to WeaponTypes.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Characters (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            rarity INTEGER NOT NULL,
            vision TEXT NOT NULL,
            weapon_type_id INTEGER NOT NULL,
            FOREIGN KEY (weapon_type_id) REFERENCES WeaponTypes (id)
        )
        """
    )
    conn.commit()

def insert_character_data(cur, conn, character_data):
    """
    Inserts character data into the Characters table with a reference to WeaponTypes.
    """
    weapon_type_id = get_weapon_type_id(cur, conn, character_data['weapon'])

    cur.execute(
        """
        INSERT OR IGNORE INTO Characters 
        (id, rarity, vision, weapon_type_id)
        VALUES (?, ?, ?, ?)
        """,
        (
            character_data['id'],
            character_data['rarity'],
            character_data['vision'],
            weapon_type_id
        )
    )
    conn.commit()


##########################--BANNERS--#################################

def get_banner_ids(banner_url):
    """
    Fetches all character banners from the API by handling pagination.

    Parameters:
    --------------------
    character_url: str
        The base URL for the API.

    limit: int
        Number of characters to fetch per request. Default is 10.

    Returns:
    --------------------
    list[int]:
        A list of character IDs retrieved from the API.
    """
    all_banners = []

    # Fetch all characters from the API (pagination can be added if needed)
    resp = requests.get(f"{banner_url}banners/")
    if resp.status_code != 200:
        print(f"Failed to fetch data: {resp.status_code}")
        return []

    data = resp.json()
    characters = data['results']

    # Take ID's and add to the larger list
    all_banners.extend([character['id'] for character in characters])

    return all_banners

def set_up_banner_table(cur, conn):
    """
    Sets up the Banners table in the SQLite database.
    """
    cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Banners (
                id INTEGER PRIMARY KEY,      -- Banner ID
                name TEXT NOT NULL,          -- Banner Name
                type TEXT NOT NULL,          -- Banner Type (e.g., Character, Weapon)
                version TEXT NOT NULL,       -- Version of the banner
                start_date TEXT NOT NULL,    -- Start date of the banner
                end_date TEXT,               -- End date of the banner
                five_star TEXT,              -- Five-star featured character name
                first_three_star TEXT,       -- First three-star featured character name
                second_three_star TEXT,      -- Second three-star featured character name
                third_three_star TEXT        -- Third three-star featured character name
            )
            """
        )
    conn.commit()
    print("Banners table created successfully!")

def insert_banner_characters(cur, conn, banner):
    """
    Inserts banner and character data into the Characters table.
    """
    banner_id = banner["id"]
    banner_name = banner["name"]
    banner_type = banner["type"]

    # Loop through featured characters and insert them into the table
    for char in banner["featured"]:
        character_id = char["id"]
        character_name = char["name"]
        try:
            cur.execute(
                """
                INSERT OR IGNORE INTO Characters (banner_id, banner_name, banner_type, character_id, character_name)
                VALUES (?, ?, ?, ?, ?)
                """,
                (banner_id, banner_name, banner_type, character_id, character_name),
            )
        except sqlite3.Error as e:
            print(f"Error inserting character {character_name}: {e}")

    conn.commit()

##########################--MAIN--#################################

def main():
    # Database setup
    cur, conn = set_up_database("genshin_impact_data.db")
    
    # Set up tables
    set_up_weapons_table(cur, conn)         # Weapons table
    set_up_character_table(cur, conn)      # Characters table
    set_up_character_weapon_table(cur, conn)  # CharactersWeapons table
    
    # API base URLs
    weapon_url = "https://genshin.jmp.blue/"
    character_url = "https://gsi.fly.dev/"
    banner_url = "https://gsi.fly.dev/"

    # Fetch and insert weapon data
    weapon_names = get_weapon_names(weapon_url)
    if weapon_names:
        weapon_list(weapon_url, weapon_names, cur, conn)
    
    # Fetch and insert character data
    character_list(character_url, cur, conn)

    # Fetch and insert character weapon data
    character_weapon_list_weapons(character_url, cur, conn)

    # Close connection
    conn.close()

if __name__ == "__main__":
    main()