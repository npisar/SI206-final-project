import sqlite3
import requests  
from bs4 import BeautifulSoup
import re

def fetch_data_from_api(url):
    """
    Fetches data from the API.
    
    Parameters
    -----------------------
    url: str
        The URL of the API to fetch data from.

    Returns
    -----------------------
    dict:
        Parsed JSON data from the API.
    """
    response = requests.get(url)
    response.raise_for_status()  # Ensure we raise an error for bad responses
    print (response.json())
    return response.json()

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
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_weapons_table(cur, conn):
    """
    Sets up the Weapons table in the database.

    cur: Cursor
        The database cursor object.

    conn: Connection
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

def set_up_characters_table(cur, conn):
    """
    Sets up the Characters table in the database.

    cur: Cursor
        The database cursor object.

    conn: Connection
        The database connection object.
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
    Sets up the Banners table in the database.

    cur: Cursor
        The database cursor object.

    conn: Connection
        The database connection object.
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

    cur: Cursor
        The database cursor object.

    conn: Connection
        The database connection object.
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



def get_artifacts():
    '''
    Fetches and processes artifacts data from the Genshin Impact wiki and handles it in increments of 25.

    ARGUMENTS:
        None

    RETURNS:
        None
    '''

    # URL for the Genshin Impact wiki page containing artifact sets
    url = "https://genshin-impact.fandom.com/wiki/Artifact_Sets"
    
    # Fetch the page
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch page, status code: {response.status_code}")

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find artifact table
    artifact_table = soup.find("table", class_="wikitable")
    if not artifact_table:
        raise ValueError("Could not find the artifact table.")
    
    rows = artifact_table.find_all("tr")
    artifact_data = []

    set_quality_pattern = r"\d"
    bonuses_pattern = r"(\d+)\sPiece:\s(.*?)(?=(\d+\sPiece:|$))"
    
    for row in rows:
        columns = row.find_all("td")
        if len(columns) < 4:  # Ensure the row has the expected number of columns
            continue

        # Get set name
        artifact_set_name = columns[0].text.strip()
        
        # Get max set quality
        set_quality = columns[1].text.strip()
        set_quality_matches = re.findall(set_quality_pattern, set_quality)
        if set_quality_matches:
            int_set_quality_matches = [int(match) for match in set_quality_matches]
            max_set_quality = max(int_set_quality_matches)
        else:
            max_set_quality = 0  # Handle case where there's no quality info
        
        # Get bonuses
        bonuses_column = columns[3].text
        bonuses_matches = re.findall(bonuses_pattern, bonuses_column)
        bonuses_list = [{"pieces": int(tup[0]), "bonus": tup[1].strip()} for tup in bonuses_matches]

        # Get the pieces column and get all pieces
        pieces_column = columns[2]
        pieces = pieces_column.find_all("span", class_="item")
        set_num_pieces = len(pieces)
    
        for piece in pieces:
            link = piece.find("a")
            if not link:
                continue

            # Get name
            artifact_name = link.get("title")

            # Get URL
            base_url = "https://genshin-impact.fandom.com"
            artifact_url = f"{base_url}{link.get('href')}"

            artifact_data.append({
                "set_name": artifact_set_name,
                "piece_1": artifact_name,  # Assuming piece_1 is the artifact name for now
                "piece_2": "",  # Modify this as necessary
                "piece_3": "",  # Modify this as necessary
                "piece_4": "",  # Modify this as necessary
                "piece_5": "",  # Modify this as necessary
                "set_bonus_2": bonuses_list[1]["bonus"] if len(bonuses_list) > 1 else "",
                "set_bonus_4": bonuses_list[3]["bonus"] if len(bonuses_list) > 3 else "",
            })
    
    # Process data in increments of 25 artifacts
    return artifact_data

def main():
    """
    Main function:
    -----------------------
    Fetches data from the API, sets up the database and tables,
    and inserts data into the tables.
    """
    # Example API URLs for your data (replace with actual API URLs)
    weapon_data = fetch_data_from_api('https://genshin.jmp.blue/weapons')
    character_data = fetch_data_from_api('https://gsi.fly.dev/characters')
    banner_data = fetch_data_from_api('https://gsi.fly.dev/banners')
    artifact_data = 
    
    
    # Scrape artifact data
    artifact_data = get_artifacts()

    #print(weapon_data)
    #print(character_data)
    #print(banner_data)
    #print(artifact_data)

    # Set up the database and tables
    cur, conn = set_up_database('genshin_impact.db')
    set_up_weapons_table(cur, conn)
    set_up_characters_table(cur, conn)
    set_up_banners_table(cur, conn)
    set_up_artifacts_table(cur, conn)

    # Insert data into the database
    insert_data_to_table(cur, conn, 'Weapons', weapon_data, ['id', 'name', 'type', 'rarity', 'base_attack', 'sub_stat', 'passive_name', 'passive_desc', 'location', 'ascension_material'])
    insert_data_to_table(cur, conn, 'Characters', character_data, ['id', 'name', 'rarity', 'weapon', 'vision'])
    insert_data_to_table(cur, conn, 'Banners', banner_data, ['name', 'type', 'version', 'start_date', 'end_date', 'featured_character', 'first_three_star', 'second_three_star', 'third_three_star'])
    
    # Insert artifact data into the Artifacts table
    insert_data_to_table(cur, conn, 'Artifacts', artifact_data, ['set_name', 'piece_1', 'piece_2', 'piece_3', 'piece_4', 'piece_5', 'set_bonus_2', 'set_bonus_4'])

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
