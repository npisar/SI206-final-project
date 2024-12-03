import json
from bs4 import BeautifulSoup
import re

'''
This file will use BS4 to scrape through the Genshin Impact Fandom Wiki Page for artifact sets. It will look at the table, and grab each one of the Pieces listed in the table. It will grab data about each artifact, then export every artifact into JSON.

Each entry in the JSON is an individual piece of each artifact set. Each piece is a span with the class "item". So for example, the first two entries are the Initiate's Flower and the Initiate's Feather. The JSON is formatted like this:

{
"name": { "Artifact Name" } (taken from the "title" attribute of each piece's <a> element)

"artifactURL": { "Artifact URL" } (taken from the "href" attribute of each piece's <a> element. It will combine the base URL https://genshin-impact.fandom.com/ with that value to make a complete link)

"artifactSet": { "Artifact Set Name" } (taken from the "name" column in the table, on the same row as the corresponding piece)

"setQuality": { "Artifact Set Quality" }  (taken from the "quality" column in the table, on the same row as the corresponding piece.)

"setBonuses": { "Artifact Set Bonuses" } (taken from the "bonuses" column in the table, on the same row as the corresponding piece. If there are multiple bonuses (like 2 or 4 piece bonuses), those are made to be two unique entries within the setBonuses entry for each piece)

"setPieceNum": { "Number of Pieces in the Set" } (a count of how many pieces are in the "pieces" column for a given artifact set (row of the table))
}

This JSON is gotten for every piece in the "pieces" column of the table listing the 54 artifact sets in the game. It outputs to a file called artifact-data.json
'''



def get_artifacts():
    '''
    ARGUMENTS:
        None

    RETURNS:
        None
    '''

    # Load the HTML file
    html_file = "APIs-and-scraping/view-source_https___genshin-impact.fandom.com_wiki_Artifact_Sets.html"
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    base_url = "https://genshin-impact.fandom.com"
    

    # Find artifact table
    artifact_table = soup.find("table", class_="wikitable")
    if not artifact_table:
        raise ValueError("Could not find the artifact table.")
    
    rows = artifact_table.find_all("tr")
    artifact_data = []
    
    set_quality_pattern = r"\d"
    bonus_pattern = r"(\d+)\sPiece:\s([^2|4|6|8|10Piece]+)"
    for row in rows:
        # print(f"row is {row}")
        columns = row.find_all("td")
        if len(columns) < 4:  # Ensure the row has the expected number of columns
            continue
    
        # get set name
        artifact_set_name = columns[0].text.strip()
        print(f"artifact set name is {artifact_set_name}")
        
        # get max set quality
        set_quality = columns[1].text.strip()
        set_quality_matches = re.findall(set_quality_pattern, set_quality)
        int_set_quality_matches = [int(match) for match in set_quality_matches]
        max_set_quality = max(int_set_quality_matches)
        print(f"max set quality is {max_set_quality}")
        
        # get bonuses
        bonuses_column = columns[3].text
        print(bonuses_column)
        bonus_matches = re.findall(bonus_pattern, bonuses_column)
        bonuses_dict = {int(num): desc.strip() for num, desc in bonus_matches}

        # get the pieces column and get all pieces
        pieces_column = columns[2]
        pieces = pieces_column.find_all("span", class_="item")
        set_num_pieces = len(pieces)
    
        for piece in pieces:
            link = piece.find("a")
            if not link:
                continue
    
            artifact_name = link.get("title")
            artifact_url = f"{base_url}{link.get('href')}"
    
            artifact_data.append({
                "name": artifact_name,
                "artifactURL": artifact_url,
                "artifactSet": artifact_set_name,
                "maxSetQuality": max_set_quality,
                "setBonuses": bonus_matches,
                "setNumPieces": set_num_pieces,
            })
    
    # Export to JSON
    output_file = "artifact-data.json"
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(artifact_data, json_file, indent=4, ensure_ascii=False)
    
    print(f"Data has been written to {output_file}")


def main():
    get_artifacts()

main()