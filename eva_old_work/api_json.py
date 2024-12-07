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

#weapons from API
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

#characters from API
def get_character_ids(character_url,):
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
        print(f"Fetching data on page {page}...")

        if resp.status_code != 200:
            print(f"Failed to fetch data: {resp.status_code}")
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

    print(all_characters)
    return all_characters

#banners from API
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
        # Data for current page
        resp = requests.get(f"{banner_url}banners?limit={limit}&page={page}")
        print(f"Fetching data on page {page}...")

        if resp.status_code != 200:
            print(f"Failed to fetch data: {resp.status_code}")
            break

        # Break open response for wanted data
        data = resp.json()
        characters = data['results']

        # Take ID's and add to the larger list
        all_banners.extend([character['id'] for character in characters])

        # Stop if there are results fewer than the limit
        if len(characters) < limit:
            break

        # Page iteration so we continue looping through them 
        page += 1

    return all_banners

#create weapons and adds it to sqlite
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

#create banner and adds it to sqlite
def banner_list(banner_url, banner_ids, cur, conn):
    """
    Fetches detailed data for each banner and stores it in the SQLite database.

    Parameters:
    --------------------
    banner_url: str
        The base URL for the API.

    banner_ids: list[int]
        A list of banner IDs to get details for.

    cur: sqlite3.Cursor
        The SQLite database cursor.

    conn: sqlite3.Connection
        The SQLite database connection.
    """
    #get the banner id's and put them through the api to get all banner information
    for banner_ids in banner_ids:
        response = requests.get(f"{banner_url}/{banner_ids}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for banner ID {banner_ids}, Status: {response.status_code}")
            continue

        banner_data = response.json()
        get_banner_ids(cur, conn, banner_data) 

#create characters and adds it to sqlite
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


#create the tables we will use use for character data
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

#create the table we will use for banenr data
def set_up_banner_table(cur, conn):
    """
    Sets up the Banners table in the SQLite database.
    """
    try:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Banners (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                version TEXT NOT NULL,
                start_date TEXT NOT NULL,  -- Column to store start date
                end_date TEXT,            -- Column to store end date
                featured_character TEXT,
                first_three_star TEXT,
                second_three_star TEXT,
                third_three_star TEXT
            )
            """
        )
        conn.commit()
        print("Banners table created successfully!")
    except sqlite3.Error as e:
        print(f"Error creating Banners table: {e}")

#create the table we will use for artifact data
def create_artifacts_table(conn, cur):
    """
    Creates the Artifacts table in the SQLite database if it doesn't already exist.

    Parameters:
    -----------------------
    conn: sqlite3.Connection
        The database connection object.
    cur: sqlite3.Cursor
        The database cursor object.

    Returns:
    -----------------------
    None
    """
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            artifactURL TEXT NOT NULL,
            artifactSetName TEXT NOT NULL,
            maxSetQuality INTEGER NOT NULL,
            setBonuses TEXT NOT NULL,
            setNumPieces INTEGER NOT NULL
        )
    """)
    conn.commit()
    print("Artifacts table created (if not already present).")


def insert_artifact_data(cur, conn):
    """
    Scrapes artifact data from the HTML file and inserts it into the Artifacts table.

    Parameters:
    -----------------------
    cur: sqlite3.Cursor
        The database cursor object.
    conn: sqlite3.Connection
        The database connection object.

    Returns:
    -----------------------
    None
    """
    # Load the HTML file
    html_file = "APIs-and-scraping/view-source_https___genshin-impact.fandom.com_wiki_Artifact_Sets.html"
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    # Find artifact table
    artifact_table = soup.find("table", class_="wikitable")
    if not artifact_table:
        raise ValueError("Could not find the artifact table.")
    
    rows = artifact_table.find_all("tr")
    set_quality_pattern = r"\d"
    bonuses_pattern = r"(\d+)\sPiece:\s(.*?)(?=(\d+\sPiece:|$))"

    for row in rows:
        columns = row.find_all("td")
        if len(columns) < 4:  # Ensure the row has the expected number of columns
            continue

        # Extract artifact set details
        artifact_set_name = columns[0].text.strip()
        set_quality = columns[1].text.strip()
        set_quality_matches = re.findall(set_quality_pattern, set_quality)
        max_set_quality = max(map(int, set_quality_matches))
        bonuses_column = columns[3].text
        bonuses_matches = re.findall(bonuses_pattern, bonuses_column)
        bonuses_list = [{"pieces": int(tup[0]), "bonus": tup[1].strip()} for tup in bonuses_matches]
        pieces_column = columns[2]
        pieces = pieces_column.find_all("span", class_="item")
        set_num_pieces = len(pieces)

        for piece in pieces:
            link = piece.find("a")
            if not link:
                continue

            # Extract individual artifact details
            artifact_name = link.get("title")
            base_url = "https://genshin-impact.fandom.com"
            artifact_url = f"{base_url}{link.get('href')}"

            # Insert data into the database
            cur.execute("""
                INSERT OR REPLACE INTO Artifacts 
                (name, artifactURL, artifactSetName, maxSetQuality, setBonuses, setNumPieces)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                artifact_name,
                artifact_url,
                artifact_set_name,
                max_set_quality,
                str(bonuses_list),  # Convert bonuses to a string to store in SQLite
                set_num_pieces
            ))
    conn.commit()
    print("Data successfully scraped and inserted into the database.")
 

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
    
    
def insert_banner_data(cur, conn, banner_data):
    """
    Inserts detailed banner data into the database.
    
    Parameters:
    --------------------
    cur: sqlite3.Cursor
        The SQLite database cursor.
    
    conn: sqlite3.Connection
        The SQLite database connection.
    
    banner_data: list[dict]
        A list of banner data to insert into the database.
    """
    for banner in banner_data:
        # Extract end date, set to NULL if absent or 'Permanent'
        end_date = None if banner.get('type') == "Permanent" else banner.get('end')

        # Extract featured characters, ensure missing characters are set to NULL
        featured = banner.get('featured', [])
        featured_character = featured[0]['name'] if len(featured) > 0 else None
        first_three_star = featured[1]['name'] if len(featured) > 1 else None
        second_three_star = featured[2]['name'] if len(featured) > 2 else None
        third_three_star = featured[3]['name'] if len(featured) > 3 else None

        # Insert the banner data into the database
        cur.execute(
            '''
            INSERT OR REPLACE INTO Banners (
                id, name, type, version, start_date, end_date, 
                featured_character, first_three_star, second_three_star, third_three_star
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                banner['id'], banner['name'], banner['type'], banner['version'], banner['start'], end_date,
                featured_character, first_three_star, second_three_star, third_three_star
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


def fetch_and_insert_banner_data(banner_url, cur, conn):
    """
    Fetches banner data and inserts it into the SQLite database.
    
    Parameters:
    --------------------
    banner_url: str
        The base URL for the API.
    
    cur: sqlite3.Cursor
        The SQLite database cursor.
    
    conn: sqlite3.Connection
        The SQLite database connection.
    """
    page = 1
    all_banners = []

    while True:
        # Fetch data for the current page
        resp = requests.get(f"{banner_url}banners?limit=25&page={page}")
        print(f"Fetching banner data on page {page}...")

        if resp.status_code != 200:
            print(f"Failed to fetch banner data: {resp.status_code}")
            break

        # Parse the response
        data = resp.json()
        banners = data['results']

        # Add fetched banner data to the list
        all_banners.extend(banners)

        # Stop pagination if there are fewer results than the limit
        if len(banners) < 25:
            break

        # Increment the page number for the next iteration
        page += 1

    # Insert banner data into the database
    insert_banner_data(cur, conn, all_banners)


def main():
    # Database setup
    cur, conn = set_up_database("genshin_impact_data.db")
    set_up_weapons_table(cur, conn)

    # API base URLs
    weapon_url = "https://genshin.jmp.blue/"
    character_url = "https://gsi.fly.dev/"
    banner_url = "https://gsi.fly.dev/"

    
    weapon_names = get_weapon_names(weapon_url)
    if weapon_names:
        weapon_list(weapon_url, weapon_names, cur, conn)
    
    set_up_character_table(cur, conn)
    for char_id in range(1, 52):
            fetch_and_insert_character(character_url, char_id, cur, conn)

    set_up_banner_table(cur, conn)
    fetch_and_insert_banner_data(banner_url, cur, conn)

    create_artifacts_table(conn, cur)
    insert_artifact_data(cur, conn)

    #to close connection
    conn.close()

if __name__ == "__main__":
    main()