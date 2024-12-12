import sqlite3
import requests

# Database Setup
def set_up_database(db_name):
    """
    Sets up a SQLite database connection and cursor

    ARGUMENTS:
    db_name: str
        The name of the SQLite database

    RETURNS:
    Tuple (Cursor, Connection):
        A tuple containing the database cursor and connection objects
    """
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    return cur, conn










##########################--MEDIA--#################################
# Get the character ids
def get_character_ids(cur):
    """
    Gets all of the character ID's from the Characters table

    ARGUMENTS:
    cur:
        SQLite cursor object

    RETURNS:
    character_ids: list
        A list containing the integer character ID's from the Characters table
    """
    character_ids = [char_id[0] for char_id in cur.execute("SELECT id FROM Characters")]
    return character_ids

# Get the media
def get_media_data(character_ids, url):
    """
    Fetches media data from the GSHIMPACT API for all character ids in the database

    ARGUMENTS:
    character_ids: list
        Every character ID from the dataset, returned from get_character_ids
    character_url: str
        The base URL for the GSHImpact API

    RETURNS:
    all_media_data: list
        List of GSHIMPACT json responses for each character ID
    """
    print(f"Media data being gathered from the GSHImpact API! Please wait...")
    all_media_data = []
    for id in character_ids:
        media_url = f"{url}characters/{id}/media"
        response = requests.get(media_url)
        
        if response.status_code == 200:
            media_data = response.json().get("result", {})
        
        all_media_data.append(media_data)
    print(f"Media API call done! Adding rows to the database...")
    return all_media_data

# Setup Media table
def setup_media_table(cur, conn):
    """
    Sets up the media table

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
        CREATE TABLE IF NOT EXISTS Media (
            character_id INTEGER,
            promotion INTEGER DEFAULT 0,
            holiday INTEGER DEFAULT 0,
            birthday INTEGER DEFAULT 0,
            videos INTEGER DEFAULT 0,
            cameos INTEGER DEFAULT 0,
            artwork INTEGER DEFAULT 0,
            FOREIGN KEY (character_id) REFERENCES Characters(id)
        )
        """
    )
    conn.commit()

# Insert the data into the Media table
def insert_media_data(media_data, start, end, limit, cur, conn):
    """
    Inserts the media data for each character into the Media table

    ARGUMENTS:
    media_data: list
        List of media data for all characters, returned from get_media_data
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
        # Get the count of items in each media type
        character_name = media_data[i]['character']['name']
        promotion_count = len(media_data[i].get("promotion", []))
        holiday_count = len(media_data[i].get("holiday", []))
        birthday_count = len(media_data[i].get("birthday", []))
        videos_count = len(media_data[i].get("videos", []))
        cameos_count = len(media_data[i].get("cameos", []))
        artwork_count = len(media_data[i].get("artwork", []))

        # Insert or update the data in the Media table
        cur.execute(
            """
            INSERT OR REPLACE INTO Media
            (character_id, promotion, holiday, birthday, videos, cameos, artwork)
            VALUES (
                (SELECT id FROM Characters WHERE name = ?),
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
    Sets up media table
    Calls functions
    Inserts information into database

    '''
    # Set up database
    cur, conn = set_up_database("data-and-tables/genshin_impact_data.db")
    
    # Set up table
    setup_media_table(cur, conn)

    # GSHImpact API base URL
    url = "https://gsi.fly.dev/"
    



    ##### Media #####
    character_ids = get_character_ids(cur)
    media_data = get_media_data(character_ids, url)

    # Insert into database
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
        print(f"All media data added to database. Please move on to calculations.py in the calculations folder!\n\n\n")
        conn.close()
        quit()
    cur.execute("SELECT max(character_id) FROM Media")
    row = cur.fetchone()
    print(f"{row[0]} / 30 total media items added to the database. Run the file again!")

    # Close connection
    conn.close()

if __name__ == "__main__":
    main()
