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









##########################--ARTIFACTS--#################################
#Create the table we will use for artifact data
def setup_artifacts_table(cur, conn):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            maxSetQuality INTEGER NOT NULL
        )
        """
    )
    conn.commit()

#Scrape and insert the artifact data into the table
def get_artifact_data(url):
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
    # # Load the HTML file
    # html_file = "APIs-and-scraping/view-source_https___genshin-impact.fandom.com_wiki_Artifact_Sets.html"
    # with open(html_file, 'r', encoding='utf-8') as file:
    #     soup = BeautifulSoup(file, 'html.parser')
    
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
    
    return all_artifact_data



def insert_artifact_data(artifact_data, start, end, limit, cur, conn):
    """
    ---
    """
    count = 0
    for i in range(start, end):
        cur.execute("""
            INSERT OR IGNORE INTO Artifacts 
            (name, maxSetQuality)
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
    # Database setup
    cur, conn = set_up_database("genshin_impact_data.db")
    
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
        print(f"All data added to database!")
        quit()

    insert_artifact_data(artifact_data=artifact_data, start=start, end=end, limit=25, cur=cur, conn=conn)
    cur.execute("SELECT max(id) FROM Artifacts")
    row = cur.fetchone()
    print(f"{row[0]} / 251 total items added")

    # CLose connection
    conn.close()

if __name__ == "__main__":
    main()
