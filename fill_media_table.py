import sqlite3
import requests
import json

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










##########################--MEDIA--#################################
#Create the media table 
# Get character ids
def get_character_ids(cur):
    character_ids = [char_id[0] for char_id in cur.execute("SELECT id FROM Characters")]
    return character_ids

#Gather media data
def get_media_data(character_ids, url):
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
    ---
    """
    all_media_data = []
    for id in character_ids:
        media_url = f"{url}characters/{id}/media"
        response = requests.get(media_url)
        
        if response.status_code == 200:
            media_data = response.json().get("result", {})
        
        all_media_data.append(media_data)
    
    return all_media_data

def setup_media_table(cur, conn):
    """
    Creates a Media table in the SQLite database with character ID as primary key
    and columns for different media types (promotion, holiday, birthday, videos, cameos, artwork).
    Each column will store the number of items in that media type.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Media (
            character_id INTEGER,
            promotion INTEGER DEFAULT 0,
            holiday INTEGER DEFAULT 0,
            birthday INTEGER DEFAULT 0,
            videos INTEGER DEFAULT 0,
            cameos INTEGER DEFAULT 0,
            artwork INTEGER DEFAULT 0,
            total_media INTEGER DEFAULT 0,
            FOREIGN KEY (character_id) REFERENCES Characters(id)
        )
        """
    )
    conn.commit()

#Insert the data into the media table
def insert_media_data(media_data, start, end, limit, cur, conn):
    """
    Inserts or updates the media data for a character into the Media table.
    """
    
    count = 0
    for i in range(start, end):
        # Get the count of items in each media type
        character_name = media_data[i]['character']['name']
        promotion_count = len(media_data[i].get("promotion", []))
        holiday_count = len(media_data[i].get("holiday", []))
        birthday_count = len(media_data[i].get("birthday", []))
        videos_count = len(media_data[i].get("videos", []))
        cameos_count = len(media_data[i].get("cameos", []))
        artwork_count = len(media_data[i].get("artwork", []))
        total_media_count = promotion_count+holiday_count+birthday_count+videos_count+cameos_count+artwork_count

        # Insert or update the data in the Media table
        cur.execute(
            """
            INSERT OR REPLACE INTO Media
            (character_id, promotion, holiday, birthday, videos, cameos, artwork, total_media)
            VALUES (
                (SELECT id FROM Characters WHERE name = ?),
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                character_name,
                promotion_count,
                holiday_count,
                birthday_count,
                videos_count,
                cameos_count,
                artwork_count,
                total_media_count
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
    
    # Set up tables
    setup_media_table(cur, conn)

    # API base URLs
    url = "https://gsi.fly.dev/"
    



    ##### Media #####
    character_ids = get_character_ids(cur)
    media_data = get_media_data(character_ids, url)

    # insert into 
    cur.execute("SELECT max(character_id) FROM Media")
    row = cur.fetchone()
    if row is None or row[0] is None:
        start = 0
        end = 25
    else:
        start = row[0]
        end = 30

    insert_media_data(media_data=media_data, start=start, end=end, limit=25, cur=cur, conn=conn)
    if start >= 25:
        print(f"All data added to database!")
        conn.close()
        quit()
    cur.execute("SELECT max(character_id) FROM Media")
    row = cur.fetchone()
    print(f"{row[0]} / 30 total items added")

    # Close connection
    conn.close()

if __name__ == "__main__":
    main()
