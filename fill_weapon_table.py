import sqlite3
import requests
import json
from bs4 import BeautifulSoup
import re

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














###################--WEAPONS--#################################
# Get the weapon data
def get_weapon_data(weapon_url):
    """
    Fetches all weapon names from the API.

    Parameters:
    --------------------
    ---
    
    Returns:
    --------------------
    ---
    """
    response = requests.get(f"{weapon_url}weapons/")
    if response.status_code != 200:
        print(f"Error fetching weapon names: {response.status_code}")
        return []
    weapon_names = response.json()
    weapon_names.remove('blackcliff-agate') # remove dupe - API limitation
    print(f"Weapon names scraped! Please wait...")

    all_weapon_data = []
    ct = 1
    for weapon_name in weapon_names:
        response = requests.get(f"{weapon_url}weapons/{weapon_name}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for weapon: {weapon_name}, Status: {response.status_code}")
            continue
        weapon_data = response.json()
        all_weapon_data.append(weapon_data)
        print(f"weapon {ct}/{len(weapon_names)} added")
        ct+=1
    print(f"scraping for weapons done!")
    return all_weapon_data

# Create the Weapons table
def setup_weapons_tables(cur, conn):
    """
    ---
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

# Insert data into weapon tables
def insert_weapon_type_data(weapon_data, cur, conn):
    """
    ---
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

# Insert the data into the weapons table
def insert_weapon_data(weapon_data, start, end, limit, cur, conn):
    """
    ---
    """
    count = 0
    for i in range(start, end):
        print(f"starting on weapon {start+count}, which is {weapon_data[i]['name']}")
        print(f"ending on {end}")
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
    # Database setup
    cur, conn = set_up_database("genshin_impact_data.db")
    
    # Set up table
    setup_weapons_tables(cur, conn)

    # API base URLs
    weapon_url = "https://genshin.jmp.blue/"
    



    ##### Weapons #####
    # weapon_data = get_weapon_data(weapon_url)

    weapon_data = []
    with open('JSON-and-old-cache-method/weapon-data.json', 'r') as file:
        data = json.load(file)
        for item in data:
            weapon_data.append(item)

    # insert into 
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
        print(f"All weapon data added to database!")
        quit()

    insert_weapon_data(weapon_data=weapon_data, start=start, end=end, limit=25, cur=cur, conn=conn)
    cur.execute("SELECT max(id) FROM Weapons")
    row = cur.fetchone()
    print(f"{row[0] + 5} / 194 total items added")

    # Close connection
    conn.close()

if __name__ == "__main__":
    main()
