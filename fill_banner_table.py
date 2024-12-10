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










##########################--BANNERS--#################################
# Get the banner data
def get_banner_data(banner_url):
    """
    Gets banner data from the GSHIMPACT API.

    Parameters:
    --------------------
    banner_url: str
        The base URL for the GSHImpact API

    Returns:
    --------------------
    all_media_data: list
        List of GSHIMPACT json responses for each banner ID
    """
    all_banner_data = []
    for banner_id in range(1, 40):  # Loop through banner IDs
        response = requests.get(f"{banner_url}banners/{banner_id}/")
        if response.status_code != 200:
            print(f"Failed to fetch data for banner ID {banner_id}, Status: {response.status_code}")
            continue

        banner_data = response.json().get('result', {})
        if not banner_data:
            print(f"No data found for banner ID {banner_id}")
            continue
        
        all_banner_data.append(banner_data)

    return all_banner_data

# Setup Banner table
def setup_banners_table(cur, conn):
    """
    Sets up the banner table

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
        CREATE TABLE IF NOT EXISTS Banners (
            id INTEGER PRIMARY KEY,
            five_star_id INTEGER,
            first_three_star_id INTEGER,
            second_three_star_id INTEGER,
            third_three_star_id INTEGER,
            FOREIGN KEY (five_star_id) REFERENCES Characters(id),
            FOREIGN KEY (first_three_star_id) REFERENCES Characters(id),
            FOREIGN KEY (second_three_star_id) REFERENCES Characters(id),
            FOREIGN KEY (third_three_star_id) REFERENCES Characters(id)
        )
        """
    )
    conn.commit()

# Insert the data into the Banners table
def insert_banner_data(banner_data, start, end, limit, cur, conn):
    """
    Inserts the media data for each character into the Media table.

    Parameters:
    --------------------
    banner_data: list
        List of data for all banners, returned from get_banner_data
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
    # Default IDs to None (or NULL) for missing characters
    five_star_name = None
    first_three_star_name = None
    second_three_star_name = None
    third_three_star_name = None
    
    count = 0
    for i in range(start, end):
        if len(banner_data[i]["featured"]) >= 1:
            five_star_name = banner_data[i]["featured"][0]["name"]
        if len(banner_data[i]["featured"]) >= 2:
            first_three_star_name = banner_data[i]["featured"][1]["name"]
        if len(banner_data[i]["featured"]) >= 3:
            second_three_star_name = banner_data[i]["featured"][2]["name"]
        if len(banner_data[i]["featured"]) >= 4:
            third_three_star_name = banner_data[i]["featured"][3]["name"]
        
        cur.execute(
            """
            INSERT OR IGNORE INTO Banners
            (five_star_id, first_three_star_id, second_three_star_id, third_three_star_id)
            VALUES (
                (SELECT id FROM Characters WHERE name = ?),
                (SELECT id FROM Characters WHERE name = ?),
                (SELECT id FROM Characters WHERE name = ?),
                (SELECT id FROM Characters WHERE name = ?)
            )
            """,
            (
                five_star_name,
                first_three_star_name,
                second_three_star_name,
                third_three_star_name
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
    setup_banners_table(cur, conn)

    # GSHIMPACT API base URL
    banner_url = "https://gsi.fly.dev/"
    



    ##### Banners #####
    banner_data = get_banner_data(banner_url)

    # Insert into database
    cur.execute("SELECT max(id) FROM Banners")
    row = cur.fetchone()
    if row is None or row[0] is None:
        start = 0
        end = 25
    else:
        start = row[0]
        end = 39

    insert_banner_data(banner_data=banner_data, start=start, end=end, limit=25, cur=cur, conn=conn)
    if start >= 25:
        print(f"All data added to database!")
        conn.close()
        quit()
    cur.execute("SELECT max(id) FROM Banners")
    row = cur.fetchone()
    print(f"{row[0]} / 39 total items added")

    # Close connection
    conn.close()

if __name__ == "__main__":
    main()
