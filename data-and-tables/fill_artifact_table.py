import sqlite3
import requests
from bs4 import BeautifulSoup
import re

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










##########################--ARTIFACTS--#################################
#Scrape and insert the artifact data into the table
def get_artifact_data(url):
    """
    Scrapes artifact data from the Genshin Impact Wiki Artifacts/Sets page and inserts it into the Artifacts table
    
    ARGUMENTS:
    url: str
        The URL of the Genshin Impact Wiki Artifacts/Sets page

    RETURNS:
    all_media_data: list
        List of data for each artifact on the Genshin Impact Wiki Artifacts/Sets page
    """
    print(f"Artifact data being gathered from https://genshin-impact.fandom.com/wiki/Artifact/Sets! Please wait...")
    # Scrape the site
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Find artifact table
    artifact_table = soup.find("table", class_="wikitable")
    if not artifact_table:
        raise ValueError("Could not find the artifact table.")
    
    rows = artifact_table.find_all("tr")
    set_quality_pattern = r"\d"

    all_artifact_data = []
    for row in rows:
        columns = row.find_all("td")
        if len(columns) < 4:  # Ensure the row has the expected number of columns
            continue

        # Extract artifact set details
        set_quality = columns[1].text.strip()
        set_quality_matches = re.findall(set_quality_pattern, set_quality)
        max_set_quality = max(map(int, set_quality_matches))
        pieces_column = columns[2]
        pieces = pieces_column.find_all("span", class_="item")

        for piece in pieces:
            link = piece.find("a")
            if not link:
                continue

            # Extract individual artifact details
            artifact_name = link.get("title")

            all_artifact_data.append({'name':artifact_name, 'max_set_quality':max_set_quality})
    print(f"Artifact web scraping done! Adding items to the database...")
    return all_artifact_data

# Setup the Artifacts table
def setup_artifacts_table(cur, conn):
    """
    Sets up the Artifacts table

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
        CREATE TABLE IF NOT EXISTS Artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            max_set_quality INTEGER NOT NULL
        )
        """
    )
    conn.commit()

def insert_artifact_data(artifact_data, start, end, limit, cur, conn):
    """
    Inserts the media data for each character into the Media table.

    ARGUMENTS:
    artifact_data: list
        List of data for all artifacts, returned from get_artifact_data
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
        cur.execute("""
            INSERT OR IGNORE INTO Artifacts 
            (name, max_set_quality)
            VALUES (
                    ?,
                    ?
            )
            """, 
            (
                artifact_data[i]['name'],
                artifact_data[i]['max_set_quality']
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
    Sets up artifact table
    Calls functions
    Inserts information into database
    '''
    # Database setup
    cur, conn = set_up_database("data-and-tables/genshin_impact_data.db")
    
    # Set up tables
    setup_artifacts_table(cur, conn)

    # BS4 base URL
    artifact_url = "https://genshin-impact.fandom.com/wiki/Artifact/Sets"
    



    ##### Weapons #####
    artifact_data = get_artifact_data(artifact_url)

    # get info and insert into 
    cur.execute("SELECT max(id) FROM Artifacts")
    row = cur.fetchone()
    if row is None or row[0] is None:
        start = 0
        end = 25
    else:
        start = row[0]
        end = 251
    if start >= 100:
        insert_artifact_data(artifact_data=artifact_data, start=start, end=end, limit=251, cur=cur, conn=conn)
        print(f"All artifact data added to database. Please move on to fill_media_table.py!\n\n\n")
        quit()

    insert_artifact_data(artifact_data=artifact_data, start=start, end=end, limit=25, cur=cur, conn=conn)
    cur.execute("SELECT max(id) FROM Artifacts")
    row = cur.fetchone()
    print(f"{row[0]} / 251 total rows of artifact data added to the database. Run the file again!\n")

    # CLose connection
    conn.close()

if __name__ == "__main__":
    main()
