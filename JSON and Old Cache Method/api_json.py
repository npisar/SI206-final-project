#eva was here

import sqlite3
import requests


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

def get_character_ids(character_url, limit=25):
    """
    Fetches all character IDs from the API by handling pagination.

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
    page = 1
    all_characters = []

    while True:
        # Fetch data for the current page
        resp = requests.get(f"{character_url}characters?limit={limit}&page={page}")
        print(f"Fetching data on page {page}...")

        if resp.status_code != 200:
            print(f"Failed to fetch data: {resp.status_code}")
            break

        # Parse the response
        data = resp.json()
        characters = data['results']

        # Extract IDs and add to the master list
        all_characters.extend([character['id'] for character in characters])

        # Stop pagination if there are fewer results than the limit
        if len(characters) < limit:
            break

        # Increment the page number for the next iteration
        page += 1

    return all_characters

def get_banner_ids(banner_url, limit=25):
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
    page = 1
    all_banners = []

    while True:
        # Fetch data for the current page
        resp = requests.get(f"{banner_url}banners?limit={limit}&page={page}")
        print(f"Fetching data on page {page}...")

        if resp.status_code != 200:
            print(f"Failed to fetch data: {resp.status_code}")
            break

        # Parse the response
        data = resp.json()
        characters = data['results']

        # Extract IDs and add to the master list
        all_banners.extend([character['id'] for character in characters])

        # Stop pagination if there are fewer results than the limit
        if len(characters) < limit:
            break

        # Increment the page number for the next iteration
        page += 1

    return all_banners


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
    for weapon_name in weapon_names:
        response = requests.get(f"{weapon_url}weapons/{weapon_name}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for weapon: {weapon_name}, Status: {response.status_code}")
            continue

        weapon_data = response.json()
        insert_weapon_data(cur, conn, weapon_data)


def banner_list(banner_url, banner_ids, cur, conn):
    """
    Fetches detailed data for each character and stores it in the SQLite database.

    Parameters:
    --------------------
    banner_url: str
        The base URL for the API.

    banner_ids: list[int]
        A list of character IDs to fetch details for.

    cur: sqlite3.Cursor
        The SQLite database cursor.

    conn: sqlite3.Connection
        The SQLite database connection.
    """
    for banner_id in banner_ids:
        response = requests.get(f"{banner_url}characters/{banner_ids}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for character ID {banner_ids}, Status: {response.status_code}")
            continue

        character_data = response.json()
        fetch_and_insert_character(cur, conn, [character_data]) 

 
def character_list(character_url, character_ids, cur, conn):
    """
    Fetches detailed data for each character and stores it in the SQLite database.

    Parameters:
    --------------------
    character_url: str
        The base URL for the API.

    character_ids: list[int]
        A list of character IDs to fetch details for.

    cur: sqlite3.Cursor
        The SQLite database cursor.

    conn: sqlite3.Connection
        The SQLite database connection.
    """
    for character_id in character_ids:
        response = requests.get(f"{character_url}characters/{character_id}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for character ID {character_id}, Status: {response.status_code}")
            continue

        character_data = response.json()
        fetch_and_insert_character(cur, conn, [character_data]) 



def set_up_weapons_table(cur, conn):
    """
    Sets up the Weapons table in the database.

    cur: sqlite3.Cursor
        The database cursor object.

    conn: sqlite3.Connection
        The database connection object.
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


def set_up_character_table(cur, conn):
    """
    Sets up the Characters table in the SQLite database.
    """
    try:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Characters (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                rarity INTEGER NOT NULL,
                weapon TEXT NOT NULL,
                vision TEXT NOT NULL
            )
            """
        )
        conn.commit()
        #print("Characters table created successfully!")
    except sqlite3.Error as e:
        print(f"Error creating Characters table: {e}")

def set_up_banner_table(cur, conn):
    """
    Sets up the banner table in the SQLite database.
    """
    try:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Banners (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type INTEGER NOT NULL,
                version TEXT NOT NULL,
                featured TEXT NOT NULL
            )
            """
        )
        conn.commit()
        print("Banners table created successfully!")
    except sqlite3.Error as e:
        print(f"Error creating Banners table: {e}")

        

def insert_weapon_data(cur, conn, weapon_data):
    """
    Inserts the detailed weapon data into the database.

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
        (id, name, type, rarity, base_attack, sub_stat, passive_name, passive_desc, location, ascension_material)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            weapon_data['id'],
            weapon_data['name'],
            weapon_data['type'],
            weapon_data['rarity'],
            weapon_data['baseAttack'],
            weapon_data['subStat'],
            weapon_data['passiveName'],
            weapon_data['passiveDesc'],
            weapon_data['location'],
            weapon_data['ascensionMaterial']
        )
    )
    conn.commit()

def insert_banner_data(cur, conn, banner_data):
    """
    Inserts the detailed weapon data into the database.

    Parameters:
    --------------------
    cur: sqlite3.Cursor
        The SQLite database cursor.

    conn: sqlite3.Connection
        The SQLite database connection.

    weapon_data: dict
        The detailed banner data to insert into the database.
    """
    cur.execute(
        """
        INSERT OR IGNORE INTO Banners 
        (id, name, type, version, featured)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            banner_data['id'],
            banner_data['name'],
            banner_data['type'],
            banner_data['version'],
            banner_data['featured'],
            
        )
    )
    conn.commit()

def fetch_and_insert_character(character_url, char_id, cur, conn):
    """
    Fetches a single character by ID and inserts it into the SQLite database.
    """
    try:
        response = requests.get(f"{character_url}characters/{char_id}")
        if response.status_code != 200:
            print(f"Character {char_id} not found (status code: {response.status_code}). Skipping...")
            return

        # Parse character data
        character = response.json().get("result", {})
        if not character:
            print(f"No data returned for character ID {char_id}. Skipping...")
            return

        # Extract relevant fields
        rarity = int(character['rarity'].split('_')[0])  # Convert "4_star" to 4
        cur.execute(
            """
            INSERT OR IGNORE INTO Characters (
                id, name, rarity, weapon, vision
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                character['id'],
                character['name'],
                rarity,
                character['weapon'],
                character['vision']
            )
        )
        conn.commit()
        #print(f"Inserted character ID {char_id}: {character['name']}")
    except sqlite3.Error as e:
        print(f"Database error while inserting character ID {char_id}: {e}")
    except Exception as e:
        print(f"Unexpected error while fetching character ID {char_id}: {e}")


def main():
    # Database setup
    cur, conn = set_up_database("genshin_impact_data.db")
    set_up_weapons_table(cur, conn)

    # API base URL
    weapon_url = "https://genshin.jmp.blue/"
    character_url = "https://gsi.fly.dev/"
    banner_url = "https://gsi.fly.dev/"

    # Fetch weapon names and store their data
    weapon_names = get_weapon_names(weapon_url)
    if weapon_names:
        weapon_list(weapon_url, weapon_names, cur, conn)
    
    set_up_character_table(cur, conn)
    for char_id in range(1, 52):
            fetch_and_insert_character(character_url, char_id, cur, conn)

    set_up_banner_table(cur, conn)
    for banner_id in range(1, 40):
            insert_banner_data(cur,conn,banner_id)

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
