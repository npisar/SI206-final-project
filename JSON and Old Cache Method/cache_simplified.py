import sqlite3
import requests

# Database Setup
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

# API call to fetch weapon names
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

# Iterator to fetch and store all weapon information
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

# Create the Weapons table
def set_up_weapons_table(cur, conn):
    """
    Sets up the Weapons table in the database with weapon_type_id, rarity, and base_attack.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Weapons (
            id TEXT PRIMARY KEY,
            weapon_type_id INTEGER NOT NULL,
            rarity INTEGER NOT NULL,
            base_attack INTEGER NOT NULL,
            FOREIGN KEY (weapon_type_id) REFERENCES WeaponTypes (id)
        )
        """
    )
    conn.commit()

# Insert weapon data into the Weapons table
def insert_weapon_data(cur, conn, weapon_data):
    """
    Inserts the detailed weapon data into the Weapons table with a reference to WeaponTypes.
    """
    # Look up the weapon type ID
    weapon_type_id = get_weapon_type_id(cur, conn, weapon_data['type'])

    # Insert the weapon data into the Weapons table
    cur.execute(
        """
        INSERT OR IGNORE INTO Weapons 
        (id, weapon_type_id, rarity, base_attack)
        VALUES (?, ?, ?, ?)
        """,
        (
            weapon_data['id'],
            weapon_type_id,
            weapon_data['rarity'],
            weapon_data['baseAttack']
        )
    )
    conn.commit()

# Create the WeaponTypes table
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

# Get the ID of a weapon type, inserting it if necessary
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

def set_up_character_table(cur, conn):
    """
    Creates the Characters table.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Characters (
            id TEXT PRIMARY KEY,
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
    Inserts character data into the Characters table.
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

def get_character_ids(character_url):
    """
    Fetches all character IDs and names from the API.
    """
    resp = requests.get(f"{character_url}characters/")
    if resp.status_code != 200:
        print(f"Failed to fetch data: {resp.status_code}")
        return []
    data = resp.json()
    return [{'id': char['id']} for char in data.get('results', [])]

def character_list(character_url, cur, conn):
    """
    Fetches and inserts detailed character data.
    """
    for char_id in range(1, 52):  # Loop through character IDs 1 to 51
        response = requests.get(f"{character_url}characters/{char_id}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for character ID {char_id}, Status: {response.status_code}")
            continue

        character_data = response.json().get('result', {})
        insert_character_data(cur, conn, character_data)

# Create the CharacterNames table
def create_character_names_table(cur, conn):
    """
    Creates a CharacterNames table with only character IDs and names.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS CharacterNames (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
        """
    )
    conn.commit()

# Inserts data into the CharacterNames table
def insert_character_names_data(cur, conn, character_data):
    """
    Inserts character IDs and names into the CharacterNames table.
    """
    cur.execute(
        """
        INSERT OR IGNORE INTO CharacterNames (id, name)
        VALUES (?, ?)
        """,
        (character_data['id'], character_data['name'])
    )
    conn.commit()

# Populate the CharacterNames table
def populate_character_names_table(character_url, cur, conn):
    """
    Fetches character data and populates the CharacterNames table.
    """
    for char_id in range(1, 52):  # Loop through character IDs 1 to 51
        response = requests.get(f"{character_url}characters/{char_id}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for character ID {char_id}, Status: {response.status_code}")
            continue

        character_data = response.json().get('result', {})
        if not character_data:
            print(f"No data for character ID {char_id}")
            continue

        # Insert into CharacterNames table
        insert_character_names_data(cur, conn, character_data)

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
    create_weapon_types_table(cur, conn)  # WeaponTypes table
    set_up_weapons_table(cur, conn)      # Weapons table
    set_up_character_table(cur, conn)   # Characters table
    create_character_names_table(cur, conn) 
    
    # API base URLs
    weapon_url = "https://genshin.jmp.blue/"
    character_url = "https://gsi.fly.dev/"

    # Fetch and insert weapon data
    weapon_names = get_weapon_names(weapon_url)
    if weapon_names:
        weapon_list(weapon_url, weapon_names, cur, conn)

    # Fetch and insert weapon data
    weapon_names = get_weapon_names(weapon_url)
    if weapon_names:
        weapon_list(weapon_url, weapon_names, cur, conn)
    
    # Fetch and insert character data
    character_list(character_url, cur, conn)
    populate_character_names_table(character_url, cur, conn)  # Populate CharacterNames table


    
    # Close connection
    conn.close()

if __name__ == "__main__":
    main()
