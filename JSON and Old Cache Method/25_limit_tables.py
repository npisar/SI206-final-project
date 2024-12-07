import sqlite3
import requests
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

    # Update progress with the new offset
    new_offset = last_offset + len(weapon_data)
    update_progress(cur, conn, "weapon_data", new_offset)

    print(f"added {len(weapon_data)} characters -- offset is now: {new_offset}")

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

# Create the CharacterVisions table
def create_character_visions_table(cur, conn):
    """
    Creates the CharacterVisions table with unique numeric IDs for each vision type.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS CharacterVisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vision TEXT UNIQUE NOT NULL
        )
        """
    )
    conn.commit()

# Get or insert a vision type and return its ID
def get_character_vision_id(cur, conn, vision):
    """
    Inserts a vision type into the CharacterVisions table if it doesn't exist and returns its ID.
    """
    cur.execute(
        """
        INSERT OR IGNORE INTO CharacterVisions (vision)
        VALUES (?)
        """,
        (vision,)
    )
    conn.commit()

    # Retrieve the ID of the vision type
    cur.execute(
        """
        SELECT id FROM CharacterVisions
        WHERE vision = ?
        """,
        (vision,)
    )
    return cur.fetchone()[0]

# Create the Characters table with vision_id
def set_up_character_table(cur, conn):
    """
    Creates the Characters table with vision_id referencing CharacterVisions.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Characters (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            rarity INTEGER NOT NULL,
            vision_id INTEGER NOT NULL,
            weapon_type_id INTEGER NOT NULL,
            FOREIGN KEY (vision_id) REFERENCES CharacterVisions (id),
            FOREIGN KEY (weapon_type_id) REFERENCES WeaponTypes (id)
        )
        """
    )
    conn.commit()

# Insert character data into Characters table
def insert_character_data(cur, conn, character_data):
    """
    Inserts character data into the Characters table, linking vision to its ID in CharacterVisions.
    """
    weapon_type_id = get_weapon_type_id(cur, conn, character_data['weapon'])
    vision_id = get_character_vision_id(cur, conn, character_data['vision'])

    cur.execute(
        """
        INSERT OR IGNORE INTO Characters 
        (id, name, rarity, vision_id, weapon_type_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            character_data['id'],
            character_data['name'],  # Include name in the Characters table
            character_data['rarity'],
            vision_id,
            weapon_type_id
        )
    )
    conn.commit()

# Populate the Characters table and CharacterVisions table
def character_list(character_url, cur, conn):
    """
    Fetches and inserts detailed character data (id, name, rarity, vision, and weapon type) into the Characters table.
    """
    for char_id in range(1, 52):  # Loop through character IDs 1 to 51
        response = requests.get(f"{character_url}characters/{char_id}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for character ID {char_id}, Status: {response.status_code}")
            continue

        character_data = response.json().get('result', {})  # Extract the 'result' field
        if not character_data:
            print(f"No data found for character ID {char_id}")
            continue

        char_id = character_data.get('id')
        char_name = character_data.get('name')  # Fetch the name of the character
        char_rarity = character_data.get('rarity', "0_star").split("_")[0]  # Extract number before '_star'
        char_rarity = int(char_rarity)  # Convert to integer
        char_vision = character_data.get('vision')
        char_weapon = character_data.get('weapon')

        # Insert the vision into CharacterVisions and the character data into Characters
        try:
            insert_character_data(
                cur, conn, 
                {
                    'id': char_id,
                    'name': char_name,  # Include name in the character data
                    'rarity': char_rarity,
                    'vision': char_vision,
                    'weapon': char_weapon
                }
            )
        except sqlite3.Error as e:
            print(f"Database error for character ID {char_id}: {e}")

##########################--BANNERS--#################################
#Create list of banners
def get_banner_list(banner_url, cur, conn):
    """
    Fetches all banners from the API by handling pagination.

    Parameters:
    --------------------
    banner_url: str
        The base URL for the banner API.

    Returns:
    --------------------
    list[dict]:
        A list of banners retrieved from the API.
    """
    all_banners = []
    for banner_id in range(1, 40):  # Loop through banner IDs
        response = requests.get(f"{banner_url}banners/{banner_id}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for banner ID {banner_id}, Status: {response.status_code}")
            continue

        banner_data = response.json().get('result', {})  # Extract the 'result' field
        if not banner_data:
            print(f"No data found for banner ID {banner_id}")
            continue
        
        all_banners.append(banner_data)  # Collect banner data into the list

    return all_banners

#Create the table of the banners
def create_banners_table(cur, conn):
    """
    Creates the Banners table in the SQLite database with character references.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Banners (
            id INTEGER PRIMARY KEY,                -- Banner ID
            five_star_id INTEGER,                  -- ID of the five-star featured character
            first_three_star_id INTEGER,           -- ID of the first three-star featured character
            second_three_star_id INTEGER,          -- ID of the second three-star featured character
            third_three_star_id INTEGER,           -- ID of the third three-star featured character
            FOREIGN KEY (five_star_id) REFERENCES Characters(id),
            FOREIGN KEY (first_three_star_id) REFERENCES Characters(id),
            FOREIGN KEY (second_three_star_id) REFERENCES Characters(id),
            FOREIGN KEY (third_three_star_id) REFERENCES Characters(id)
        )
        """
    )
    conn.commit()

#Insert the data into the banners table
def insert_banners(cur, conn, banner):
    """
    Inserts the banner data into the Banners table, linking it to featured characters.
    """
    banner_id = banner["id"]
    
    # Default IDs to None (or NULL) for missing characters
    five_star_id = None
    first_three_star_id = None
    second_three_star_id = None
    third_three_star_id = None
    
    if len(banner["featured"]) >= 1:
        five_star_id = banner["featured"][0]["id"]
    if len(banner["featured"]) >= 2:
        first_three_star_id = banner["featured"][1]["id"]
    if len(banner["featured"]) >= 3:
        second_three_star_id = banner["featured"][2]["id"]
    if len(banner["featured"]) >= 4:
        third_three_star_id = banner["featured"][3]["id"]
        
    try:
        cur.execute(
            """
            INSERT OR IGNORE INTO Banners (
                 id, five_star_id, first_three_star_id, second_three_star_id, third_three_star_id
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (banner_id, five_star_id, first_three_star_id, second_three_star_id, third_three_star_id)
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting banner {banner_id}: {e}")

##########################--MEDIA--#################################
#Gather media data
def get_media_data(character_id, character_url):
    """
    Fetches media data for a specific character from the API.

    Parameters:
    --------------------
    character_id: int
        The character's unique ID.
    character_url: str
        The base URL for the character API.

    Returns:
    --------------------
    dict: A dictionary containing media data, including videos, cameos, artwork, etc.
    """
    media_url = f"{character_url}characters/{character_id}/media"
    response = requests.get(media_url)
    
    if response.status_code == 200:
        return response.json().get("result", {})
    else:
        print(f"Failed to fetch media data for character ID {character_id}, Status: {response.status_code}")
        return {}

#Create the media table 
def create_media_table(cur, conn):
    """
    Creates a Media table in the SQLite database with character ID as primary key
    and columns for different media types (promotion, holiday, birthday, videos, cameos, artwork).
    Each column will store the number of items in that media type.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Media (
            id INTEGER PRIMARY KEY,                -- Character ID
            promotion INTEGER DEFAULT 0,            -- Number of promotion items
            holiday INTEGER DEFAULT 0,              -- Number of holiday items
            birthday INTEGER DEFAULT 0,             -- Number of birthday items
            videos INTEGER DEFAULT 0,               -- Number of video items
            cameos INTEGER DEFAULT 0,               -- Number of cameo items
            artwork INTEGER DEFAULT 0               -- Number of artwork items
        )
        """
    )
    conn.commit()
    print("Media table created successfully!")

#Insert the data into the media table
def insert_media_data(cur, conn, character_id, media_data):
    """
    Inserts or updates the media data for a character into the Media table.
    """
    try:
        # Get the count of items in each media type
        promotion_count = len(media_data.get("promotion", []))
        holiday_count = len(media_data.get("holiday", []))
        birthday_count = len(media_data.get("birthday", []))
        videos_count = len(media_data.get("videos", []))
        cameos_count = len(media_data.get("cameos", []))
        artwork_count = len(media_data.get("artwork", []))

        # Insert or update the data in the Media table
        cur.execute(
            """
            INSERT OR REPLACE INTO Media (
                id, promotion, holiday, birthday, videos, cameos, artwork
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (character_id, promotion_count, holiday_count, birthday_count, videos_count, cameos_count, artwork_count)
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting media data for character ID {character_id}: {e}")

##########################--ARTIFACTS--#################################
#Create the table we will use for artifact data
def create_artifacts_table(conn, cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Artifacts (
        artifact_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        maxSetQuality INTEGER NOT NULL
    );
    """)
    conn.commit()

#Scrape and insert the artifact data into the table
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
                (name, maxSetQuality)
                VALUES (?, ?)
            """, (
                artifact_name,
                max_set_quality,
            ))
    conn.commit()
    print("Data successfully scraped and inserted into the database.")

##########################--MAIN--#################################

def main():
    # Database setup
    cur, conn = set_up_database("genshin_impact_data.db")
    
    # Set up tables
    create_weapon_types_table(cur, conn)  # WeaponTypes table
    set_up_weapons_table(cur, conn)      # Weapons table
    create_character_visions_table(cur, conn)  # CharacterVisions table
    set_up_character_table(cur, conn)   # Characters table
    create_banners_table(cur, conn)      # Banners table
    create_media_table(cur, conn)        # Media table

    # API base URLs
    weapon_url = "https://genshin.jmp.blue/"
    character_url = "https://gsi.fly.dev/"
    banner_url = "https://gsi.fly.dev/"  # Adjust according to your actual banner API URL

    # Fetch and insert weapon data
    weapon_names = get_weapon_names(weapon_url)
    if weapon_names:
        weapon_list(weapon_url, weapon_names, cur, conn)
    
    # Fetch and insert character data
    character_list(character_url, cur, conn)  # Populates CharacterVisions and Characters
    
    # Fetch and insert banner data
    banners = get_banner_list(banner_url, cur, conn)
    for banner in banners:
        insert_banners(cur, conn, banner)

    # Fetch and insert media data for each character
    for character_id in range(1, 40):  # Loop through character IDs (or use a different range if necessary)
        media_data = get_media_data(character_id, character_url)
        if media_data:
            insert_media_data(cur, conn, character_id, media_data)

    create_artifacts_table(conn, cur)
    insert_artifact_data(cur, conn)
    
    # Close connection
    conn.close()

if __name__ == "__main__":
    main()
