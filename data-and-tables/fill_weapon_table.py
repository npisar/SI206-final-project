import sqlite3
import requests
from bs4 import BeautifulSoup

# Database Setup
def set_up_database(db_name):
    """
    Sets up a SQLite database connection and cursor

    ARGUMENTS:
    -----------------------
    db_name: str
        The name of the SQLite database

    RETURNS:
    -----------------------
    Tuple (Cursor, Connection):
        A tuple containing the database cursor and connection objects
    """
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    return cur, conn










###################--WEAPONS--#################################
# Get the weapon data
def get_weapon_data(weapon_url):
    """
    Gets weapon data from the Genshin.dev for all character ids in the database

    ARGUMENTS:
    weapon_url: str
        The base URL for the Genshin.dev API

    RETURNS:
    all_media_data: list
        List of Genshin.dev json responses for each weapon
    """
    print(f"Weapon data being gathered from the Genshin.dev API! Please wait...")
    response = requests.get(f"{weapon_url}weapons/")
    if response.status_code != 200:
        print(f"Error fetching weapon names: {response.status_code}")
        return []
    weapon_names = response.json()
    weapon_names.remove('blackcliff-agate') # remove dupe - API limitation

    all_weapon_data = []
    # ct = 1    # used for development
    for weapon_name in weapon_names:
        response = requests.get(f"{weapon_url}weapons/{weapon_name}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for weapon: {weapon_name}, Status: {response.status_code}")
            continue
        weapon_data = response.json()
        all_weapon_data.append(weapon_data)
        # print(f"Data for {ct}/{len(weapon_names)} weapons gathered")    # used for development
        # ct+=1    # used for development
    print(f"Weapon API call done! Adding rows to the database...")
    return all_weapon_data

# Create the Weapons table
def setup_weapons_tables(cur, conn):
    """
    Sets up the Weapons and WeaponTypes table

    ARGUMENTS:
    cur:
        SQLite cursor object
    conn:
        SQLite connection object

    RETURNS:
    None
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Weapons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            weapon_type_id INTEGER,
            rarity INTEGER NOT NULL,
            base_attack INTEGER NOT NULL,
            FOREIGN KEY (weapon_type_id) REFERENCES WeaponTypes (id)
        )
        """
    )
    conn.commit()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS WeaponTypes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            weapon_type TEXT UNIQUE NOT NULL
        )
        """
    )
    conn.commit()

# Insert the weapon type data into the WeaponTypes table
def insert_weapon_type_data(weapon_data, cur, conn):
    """
    Inserts the weapon type data into the WeaponTypes table

    ARGUMENTS:
    weapon_data: list
        List of data for all weapons, returned from get_weapon_data
    cur:
        SQLite cursor
    conn:
        SQLite connection
    
    RETURNS:
        None
    """

    weapon_types = []
    for weapon in weapon_data:
        if weapon['type'] not in weapon_types:
            weapon_types.append(weapon['type'])
        if len(weapon_types) == 5:
            break
        else:
            continue

    for weapon_type in weapon_types:
        cur.execute(
            """
            INSERT OR IGNORE INTO WeaponTypes (weapon_type)
            VALUES (?)
            """,
            (weapon_type, )
        )
        conn.commit()

# Insert the data into the Weapons table
def insert_weapon_data(weapon_data, start, end, limit, cur, conn):
    """
    Inserts the weapon data into the Weapons table

    ARGUMENTS:
    weapon_data: list
        List of data for all weapons, returned from get_weapon_data
    start: int
        Integer starting point which to iterate from (remembers where it left off)
    end: int
        Integer upper bound of where to iterate through (maximum number of items the API supplies)
    limit: int
        Integer limit of how many items can be returned
    cur:
        SQLite cursor object
    conn:
        SQLite connection object
    
    RETURNS:
        None
    """
    count = 0
    for i in range(start, end):
        # print(f"starting on weapon {start+count}, which is {weapon_data[i]['name']}")
        cur.execute(
            """ 
            INSERT OR IGNORE INTO Weapons 
            (name, weapon_type_id, rarity, base_attack)
            VALUES (
                ?,
                (SELECT id FROM WeaponTypes WHERE weapon_type = ?), 
                ?, 
                ?
            )
            """,
            (
                weapon_data[i]['name'],
                weapon_data[i]['type'],
                weapon_data[i]['rarity'],
                weapon_data[i]['baseAttack']
            )
        )
        conn.commit()
        if cur.rowcount != 0:
            count += 1
        if count == limit:
            break










##########################--MAIN--#################################

def main():
    '''
    Sets up database 
    Sets up weapons tables
    Calls functions
    Inserts information into database
    '''
    # Database setup
    cur, conn = set_up_database("data-and-tables/genshin_impact_data.db")
    
    # Set up table
    setup_weapons_tables(cur, conn)

    # Genshin.dev base URL
    weapon_url = "https://genshin.jmp.blue/"
    



    ##### Weapons #####
    weapon_data = get_weapon_data(weapon_url)

    # Insert into database
    cur.execute("SELECT max(id) FROM Weapons")
    row = cur.fetchone()
    if row is None or row[0] is None:
        insert_weapon_type_data(weapon_data, cur, conn)
        start = 0
        end = 20
    else:
        start = row[0]
        end = 187
    if start >= 95:
        insert_weapon_data(weapon_data=weapon_data, start=start, end=end, limit=200, cur=cur, conn=conn)
        print(f"All weapon data added to the database. Please move on to fill_character_table.py!\n\n\n")
        quit()

    insert_weapon_data(weapon_data=weapon_data, start=start, end=end, limit=25, cur=cur, conn=conn)
    cur.execute("SELECT max(id) FROM Weapons")
    row = cur.fetchone()
    print(f"{row[0] + 5} / 194 total rows of weapon data added to the database. Run the file again!\n")

    # Close connection
    conn.close()

if __name__ == "__main__":
    main()
