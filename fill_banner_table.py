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
            vision_id INTEGER NOT NULL
        )
        """
    )
    conn.commit()


# Get the ID of a weapon type, inserting it if necessary
def insert_weapon_type_table(weapon_data, cur, conn):
    """
    Inserts a weapon type if it doesn't exist and returns its ID.
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




























# ##########################--BANNERS--#################################
# #Create list of banners
# def get_banner_list(banner_url, cur, conn):
#     """
#     Fetches all banners from the API by handling pagination.

#     Parameters:
#     --------------------
#     banner_url: str
#         The base URL for the banner API.

#     Returns:
#     --------------------
#     list[dict]:
#         A list of banners retrieved from the API.
#     """
#     all_banners = []
#     for banner_id in range(1, 40):  # Loop through banner IDs
#         response = requests.get(f"{banner_url}banners/{banner_id}/")
#         if response.status_code != 200:
#             print(f"Failed to fetch data for banner ID {banner_id}, Status: {response.status_code}")
#             continue

#         banner_data = response.json().get('result', {})  # Extract the 'result' field
#         if not banner_data:
#             print(f"No data found for banner ID {banner_id}")
#             continue
        
#         all_banners.append(banner_data)  # Collect banner data into the list

#     return all_banners

# #Create the table of the banners
# def create_banners_table(cur, conn):
#     """
#     Creates the Banners table in the SQLite database with character references.
#     """
#     cur.execute(
#         """
#         CREATE TABLE IF NOT EXISTS Banners (
#             id INTEGER PRIMARY KEY,                -- Banner ID
#             five_star_id INTEGER,                  -- ID of the five-star featured character
#             first_three_star_id INTEGER,           -- ID of the first three-star featured character
#             second_three_star_id INTEGER,          -- ID of the second three-star featured character
#             third_three_star_id INTEGER,           -- ID of the third three-star featured character
#             FOREIGN KEY (five_star_id) REFERENCES Characters(id),
#             FOREIGN KEY (first_three_star_id) REFERENCES Characters(id),
#             FOREIGN KEY (second_three_star_id) REFERENCES Characters(id),
#             FOREIGN KEY (third_three_star_id) REFERENCES Characters(id)
#         )
#         """
#     )
#     conn.commit()

# #Insert the data into the banners table
# def insert_banners(cur, conn, banner):
#     """
#     Inserts the banner data into the Banners table, linking it to featured characters.
#     """
#     banner_id = banner["id"]
    
#     # Default IDs to None (or NULL) for missing characters
#     five_star_id = None
#     first_three_star_id = None
#     second_three_star_id = None
#     third_three_star_id = None
    
#     if len(banner["featured"]) >= 1:
#         five_star_id = banner["featured"][0]["id"]
#     if len(banner["featured"]) >= 2:
#         first_three_star_id = banner["featured"][1]["id"]
#     if len(banner["featured"]) >= 3:
#         second_three_star_id = banner["featured"][2]["id"]
#     if len(banner["featured"]) >= 4:
#         third_three_star_id = banner["featured"][3]["id"]
        
#     try:
#         cur.execute(
#             """
#             INSERT OR IGNORE INTO Banners (
#                  id, five_star_id, first_three_star_id, second_three_star_id, third_three_star_id
#             ) VALUES (?, ?, ?, ?, ?)
#             """,
#             (banner_id, five_star_id, first_three_star_id, second_three_star_id, third_three_star_id)
#         )
#         conn.commit()
#     except sqlite3.Error as e:
#         print(f"Error inserting banner {banner_id}: {e}")


























# ##########################--MEDIA--#################################
# #Gather media data
# def get_media_data(character_id, character_url):
#     """
#     Fetches media data for a specific character from the API.

#     Parameters:
#     --------------------
#     character_id: int
#         The character's unique ID.
#     character_url: str
#         The base URL for the character API.

#     Returns:
#     --------------------
#     dict: A dictionary containing media data, including videos, cameos, artwork, etc.
#     """
#     media_url = f"{character_url}characters/{character_id}/media"
#     response = requests.get(media_url)
    
#     if response.status_code == 200:
#         return response.json().get("result", {})
#     else:
#         print(f"Failed to fetch media data for character ID {character_id}, Status: {response.status_code}")
#         return {}

# #Create the media table 
# def create_media_table(cur, conn):
#     """
#     Creates a Media table in the SQLite database with character ID as primary key
#     and columns for different media types (promotion, holiday, birthday, videos, cameos, artwork).
#     Each column will store the number of items in that media type.
#     """
#     cur.execute(
#         """
#         CREATE TABLE IF NOT EXISTS Media (
#             id INTEGER PRIMARY KEY,                -- Character ID
#             promotion INTEGER DEFAULT 0,            -- Number of promotion items
#             holiday INTEGER DEFAULT 0,              -- Number of holiday items
#             birthday INTEGER DEFAULT 0,             -- Number of birthday items
#             videos INTEGER DEFAULT 0,               -- Number of video items
#             cameos INTEGER DEFAULT 0,               -- Number of cameo items
#             artwork INTEGER DEFAULT 0               -- Number of artwork items
#         )
#         """
#     )
#     conn.commit()
#     print("Media table created successfully!")

# #Insert the data into the media table
# def insert_media_data(cur, conn, character_id, media_data):
#     """
#     Inserts or updates the media data for a character into the Media table.
#     """
#     try:
#         # Get the count of items in each media type
#         promotion_count = len(media_data.get("promotion", []))
#         holiday_count = len(media_data.get("holiday", []))
#         birthday_count = len(media_data.get("birthday", []))
#         videos_count = len(media_data.get("videos", []))
#         cameos_count = len(media_data.get("cameos", []))
#         artwork_count = len(media_data.get("artwork", []))

#         # Insert or update the data in the Media table
#         cur.execute(
#             """
#             INSERT OR REPLACE INTO Media (
#                 id, promotion, holiday, birthday, videos, cameos, artwork
#             ) VALUES (?, ?, ?, ?, ?, ?, ?)
#             """,
#             (character_id, promotion_count, holiday_count, birthday_count, videos_count, cameos_count, artwork_count)
#         )
#         conn.commit()
#     except sqlite3.Error as e:
#         print(f"Error inserting media data for character ID {character_id}: {e}")






















# ##########################--ARTIFACTS--#################################
# #Create the table we will use for artifact data
# def create_artifacts_table(conn, cur):
#     cur.execute("""
#     CREATE TABLE IF NOT EXISTS Artifacts (
#         artifact_id INTEGER PRIMARY KEY,
#         name TEXT NOT NULL,
#         maxSetQuality INTEGER NOT NULL
#     );
#     """)
#     conn.commit()

# #Scrape and insert the artifact data into the table
# def insert_artifact_data(cur, conn):
#     """
#     Scrapes artifact data from the HTML file and inserts it into the Artifacts table.

#     Parameters:
#     -----------------------
#     cur: sqlite3.Cursor
#         The database cursor object.
#     conn: sqlite3.Connection
#         The database connection object.

#     Returns:
#     -----------------------
#     None
#     """
#     # Load the HTML file
#     html_file = "APIs-and-scraping/view-source_https___genshin-impact.fandom.com_wiki_Artifact_Sets.html"
#     with open(html_file, 'r', encoding='utf-8') as file:
#         soup = BeautifulSoup(file, 'html.parser')
    
#     # Find artifact table
#     artifact_table = soup.find("table", class_="wikitable")
#     if not artifact_table:
#         raise ValueError("Could not find the artifact table.")
    
#     rows = artifact_table.find_all("tr")
#     set_quality_pattern = r"\d"
#     bonuses_pattern = r"(\d+)\sPiece:\s(.*?)(?=(\d+\sPiece:|$))"

#     for row in rows:
#         columns = row.find_all("td")
#         if len(columns) < 4:  # Ensure the row has the expected number of columns
#             continue

#         # Extract artifact set details
#         artifact_set_name = columns[0].text.strip()
#         set_quality = columns[1].text.strip()
#         set_quality_matches = re.findall(set_quality_pattern, set_quality)
#         max_set_quality = max(map(int, set_quality_matches))
#         bonuses_column = columns[3].text
#         bonuses_matches = re.findall(bonuses_pattern, bonuses_column)
#         bonuses_list = [{"pieces": int(tup[0]), "bonus": tup[1].strip()} for tup in bonuses_matches]
#         pieces_column = columns[2]
#         pieces = pieces_column.find_all("span", class_="item")
#         set_num_pieces = len(pieces)

#         for piece in pieces:
#             link = piece.find("a")
#             if not link:
#                 continue

#             # Extract individual artifact details
#             artifact_name = link.get("title")
#             base_url = "https://genshin-impact.fandom.com"
#             artifact_url = f"{base_url}{link.get('href')}"

#             # Insert data into the database
#             cur.execute("""
#                 INSERT OR REPLACE INTO Artifacts 
#                 (name, maxSetQuality)
#                 VALUES (?, ?)
#             """, (
#                 artifact_name,
#                 max_set_quality,
#             ))
#     conn.commit()
#     print("Data successfully scraped and inserted into the database.")
























##########################--MAIN--#################################

def main():
    # Database setup
    cur, conn = set_up_database("genshin_impact_data.db")
    
    # Set up tables
    setup_weapons_tables(cur, conn)
    
    # create_character_visions_table(cur, conn)  # CharacterVisions table
    # set_up_character_table(cur, conn)          # Characters table
    
    # create_banners_table(cur, conn)            # Banners table
    # create_media_table(cur, conn)              # Media table

    # API base URLs
    weapon_url = "https://genshin.jmp.blue/"
    character_url = "https://gsi.fly.dev/"
    banner_url = "https://gsi.fly.dev/"
    



    ##### Weapons #####
    # weapon_data = get_weapon_data(weapon_url)

    weapon_data = []
    with open('JSON-and-old-cache-method/weapon-data.json', 'r') as file:
        data = json.load(file)
        for item in data:
            weapon_data.append(item)


    # Check if the weapons type table exists
    cur.execute("SELECT max(id) FROM WeaponTypes")
    table_exists = cur.fetchone()
    if not table_exists:
        
        quit()

    # insert into 
    cur.execute("SELECT max(id) FROM Weapons")
    row = cur.fetchone()
    if row is None or row[0] is None:
        insert_weapon_type_table(weapon_data, cur, conn)
        start = 0
        end = 20
    else:
        start = row[0]
        end = 187
    if start >= 95:
        insert_weapon_data(weapon_data=weapon_data, start=start, end=end, limit=200, cur=cur, conn=conn)
        print(f"All data added to database!")
        quit()

    insert_weapon_data(weapon_data=weapon_data, start=start, end=end, limit=25, cur=cur, conn=conn)
    cur.execute("SELECT max(id) FROM Weapons")
    row = cur.fetchone()
    print(f"{row[0] + 5} / 194 total items added")










    # # Fetch and insert character data
    # character_list(character_url, cur, conn)  # Populates CharacterVisions and Characters
    
    # # Fetch and insert banner data
    # banners = get_banner_list(banner_url, cur, conn)
    # for banner in banners:
    #     insert_banners(cur, conn, banner)

    # # Fetch and insert media data for each character
    # for character_id in range(1, 40):  # Loop through character IDs (or use a different range if necessary)
    #     media_data = get_media_data(character_id, character_url)
    #     if media_data:
    #         insert_media_data(cur, conn, character_id, media_data)

    # create_artifacts_table(conn, cur)
    # insert_artifact_data(cur, conn)
    
    # Close connection
    conn.close()

if __name__ == "__main__":
    main()
