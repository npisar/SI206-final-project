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
























##########################--CHARACTERS--#################################
def get_character_data(character_url):
    """
    Gets character data from the GSHIMPACT API.

    Parameters:
    --------------------
    character_url: str
        The base URL for the GSHImpact API

    Returns:
    --------------------
    all_media_data: list
        List of GSHIMPACT json responses for each character ID
    """
    print(f"Character data being gathered from the GSHImpact API! Please wait...")
    all_character_data = []
    for char_id in range(1, 52):  # Loop through character IDs 1 to 51
        response = requests.get(f"{character_url}characters/{char_id}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for character ID {char_id}, Status: {response.status_code}")
            continue

        character_data = response.json().get('result', {})  # Extract the 'result' field
        if not character_data:
            print(f"No data found for character ID {char_id}")
            continue

        name = character_data.get('name')  # Fetch the name of the character
        rarity = character_data.get('rarity', "0_star").split("_")[0]  # Extract number before '_star'
        rarity = int(rarity)  # Convert to integer
        vision = character_data.get('vision')
        weapon = character_data.get('weapon')

        all_character_data.append({'name':name, 'rarity':rarity, 'vision':vision, 'weapon':weapon})
    print(f"Character API call done! Adding items to the database...")
    return all_character_data

# Setup Character tables
def setup_character_tables(cur, conn):
    """
    Sets up the Characters and CharacterVisions table

    Parameters:
    --------------------
    cur:
        SQLite cursor object
    conn:
        SQLite connection object

    Returns:
    --------------------
    None
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rarity INTEGER NOT NULL,
            vision_id INTEGER,
            weapon_id INTEGER,
            FOREIGN KEY (vision_id) REFERENCES CharacterVisions (id),
            FOREIGN KEY (weapon_id) REFERENCES WeaponTypes (id)
        )
        """
    )
    conn.commit()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS CharacterVisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vision TEXT UNIQUE NOT NULL
        )
        """
    )
    conn.commit()

# Insert the character visions data into the CharacterVisions table
def insert_character_vision_table(character_data, cur, conn):
    """
    Inserts the character visions data into the CharacterVisions table.

    Parameters:
    --------------------
    character_data: list
        List of data for all characters, returned from get_character_data
    cur:
        SQLite cursor
    conn:
        SQLite connection
    
    Returns: none
    --------------------
    """

    character_visions = []
    for character in character_data:
        # print(f"char vision is {character['vision']}")
        if character['vision'] not in character_visions:
            character_visions.append(character['vision'])
        if len(character_visions) == 7:
            break
        else:
            continue

    for vision in character_visions:
        cur.execute(
            """
            INSERT OR IGNORE INTO CharacterVisions (vision)
            VALUES (?)
            """,
            (vision, )
        )
        conn.commit()


# Insert character data into Characters table
def insert_character_data(character_data, start, end, limit, cur, conn):
    """
    Inserts the character data into the Characters table.

    Parameters:
    --------------------
    character_data: list
        List of data for all characters, returned from get_character_data
    start: int
        starting point which to iterate through (remembers where it left off)
    end: int
        upper bound of where to iterate through (maximum number of items the API supplies)
    limit: int
        limit of how many items can be returned
    cur:
        SQLite cursor
    conn:
        SQLite connection
    
    Returns:
    --------------------
    None
    """
    count = 0
    for i in range(start, end):
        # print(f"Adding character {start+count}, which is {character_data[i]['name']}")
        # print(f"ending on {end}")
        cur.execute(
            """ 
            INSERT OR IGNORE INTO Characters 
            (name, rarity, vision_id, weapon_id)
            VALUES (
                ?,
                ?,
                (SELECT id FROM CharacterVisions WHERE vision = ?),
                (SELECT id FROM WeaponTypes WHERE weapon_type = ?)
            )
            """,
            (
                character_data[i]['name'],
                character_data[i]['rarity'],
                character_data[i]['vision'],
                character_data[i]['weapon']
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
    cur, conn = set_up_database("data-and-tables/genshin_impact_data.db")
    
    # Set up tables
    setup_character_tables(cur, conn)

    # API base URLs
    character_url = "https://gsi.fly.dev/"
    



    ##### characters #####
    character_data = get_character_data(character_url)

    # insert into 
    cur.execute("SELECT max(id) FROM Characters")
    row = cur.fetchone()
    if row is None or row[0] is None:
        insert_character_vision_table(character_data, cur, conn)
        start = 0
        end = 18
    else:
        start = row[0]
        end = 51

    insert_character_data(character_data=character_data, start=start, end=end, limit=25, cur=cur, conn=conn)
    if start >= 43:
        print(f"All character data added to the database. Please move on to fill_banner_table.py!\n\n\n")
        quit()
    cur.execute("SELECT max(id) FROM Characters")
    row = cur.fetchone()
    print(f"{row[0] + 7} / 58 total rows of character data added to the database. Run the file again!\n")

    
    # Close connection
    conn.close()

if __name__ == "__main__":
    main()
