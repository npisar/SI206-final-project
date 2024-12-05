# eva was here 

# 25 limit testing section

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

def set_up_progress_table(cur, conn):
    """
    Sets up a Progress table to track the progress of data insertion for each resource.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Progress (
            resource TEXT PRIMARY KEY,
            last_offset INTEGER NOT NULL
        )
        """
    )
    conn.commit()

def update_progress(cur, conn, resource, offset):
    """
    Updates the progress table with the latest offset for a given resource.
    """
    cur.execute(
        """
        INSERT OR REPLACE INTO Progress (resource, last_offset)
        VALUES (?, ?)
        """,
        (resource, offset)
    )
    conn.commit()

def get_last_offset(cur, resource):
    """
    Fetches the last offset for a given resource from the Progress table.
    """
    cur.execute("SELECT last_offset FROM Progress WHERE resource = ?", (resource,))
    result = cur.fetchone()
    return result[0] if result else 0


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
        # Data for current page
        resp = requests.get(f"{character_url}characters?limit={limit}&page={page}")
        print(f"retrieving data on page {page}...")

        if resp.status_code != 200:
            print(f"failed to retrieve data: {resp.status_code}")
            break

        # Break open response for wanted data
        data = resp.json()
        characters = data['results']

        # Take ID's and add to the larger list
        all_characters.extend([character['id'] for character in characters])

        # Stop if there are fewer results than the limit
        if len(characters) < limit:
            break

        # Page iteration so we continue looping through pages
        page += 1

    return all_characters

def fetch_and_insert_character_data(character_url, cur, conn, limit=25):
    """
    Fetches character data in batches and inserts into the database.
    Resumes from the last offset if available.
    """
    # Get the last offset from the progress table
    last_offset = get_last_offset(cur, "characters")
    page = last_offset // limit + 1  # Determine which page to start from

    # Fetch a batch of character data
    resp = requests.get(f"{character_url}characters?limit={limit}&page={page}")
    if resp.status_code != 200:
        print(f"Failed to fetch character data: {resp.status_code}")
        return

    # Parse response and insert data
    data = resp.json()
    characters = data.get("results", [])
    for character in characters:
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

    # Update progress with the new offset
    new_offset = last_offset + len(characters)
    update_progress(cur, conn, "characters", new_offset)

    print(f"added {len(characters)} characters -- offset is now: {new_offset}")


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
    #get the character id's and put them through the api to get all character information
    for character_id in character_ids:
        response = requests.get(f"{character_url}characters/{character_id}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for character ID {character_id}, Status: {response.status_code}")
            continue

        character_data = response.json()
        fetch_and_insert_character(cur, conn, [character_data]) 



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




def main():
    # Database setup
    cur, conn = set_up_database("genshin_impact_data_test.db")
    set_up_progress_table(cur, conn)

    # API base URLs
    weapon_url = "https://genshin.jmp.blue/"
    character_url = "https://gsi.fly.dev/"
    banner_url = "https://gsi.fly.dev/"

    # Fetch and insert data in batches
    set_up_character_table(cur, conn)
    fetch_and_insert_character_data(character_url, cur, conn, limit=25)


    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
