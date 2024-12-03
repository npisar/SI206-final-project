import json
from bs4 import BeautifulSoup
import re

'''
This file will use BS4 to scrape through the Genshin Impact Fandom Wiki Page for artifact sets. It will look at the table, and grab each one of the Pieces listed in the table. It will grab data about each artifact, then export every artifact into JSON.

Each entry in the JSON is an individual piece of each artifact set. Each piece is a span with the class "item". So for example, the first two entries are the Initiate's Flower and the Initiate's Feather. The JSON is formatted like this:

{
    "name": { "Artifact Name" } (str. taken from the "title" attribute of each piece's <a> element)

    "artifactURL": { "Artifact URL" } (str. taken from the "href" attribute of each piece's <a> element. It will combine the base URL https://genshin-impact.fandom.com/ with that value to make a complete link)

    "artifactSet": { "Artifact Set Name" } (str. taken from the "name" column in the table, on the same row as the corresponding piece)

    "maxSetQuality": { "Max Artifact Set Quality" }  (int. taken from the "quality" column in the table, on the same row as the corresponding piece. it takes the max of the star ranges given in the table)

    "setBonuses": { "Artifact Set Bonuses" } (dict. taken from the "bonuses" column in the table, on the same row as the corresponding piece.)

    "setNumPieces": { "Number of Pieces in the Set" } (int. a count of how many pieces are in the "pieces" column for a given artifact set (row of the table))
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
    

    # Find artifact table
    artifact_table = soup.find("table", class_="wikitable")
    if not artifact_table:
        raise ValueError("Could not find the artifact table.")
    
    rows = artifact_table.find_all("tr")
    artifact_data = []
    
    set_quality_pattern = r"\d"
    bonuses_pattern = r"(\d+)\sPiece:\s(.*?)(?=(\d+\sPiece:|$))"
    for row in rows:
        # print(f"row is {row}")
        columns = row.find_all("td")
        if len(columns) < 4:  # Ensure the row has the expected number of columns
            continue
    
        # get set name
        artifact_set_name = columns[0].text.strip()
        # print(f"artifact set name is {artifact_set_name}")
        
        # get max set quality
        set_quality = columns[1].text.strip()
        set_quality_matches = re.findall(set_quality_pattern, set_quality)
        int_set_quality_matches = [int(match) for match in set_quality_matches]
        max_set_quality = max(int_set_quality_matches)
        # print(f"max set quality is {max_set_quality}")
        
        # get bonuses
        bonuses_column = columns[3].text
        print(bonuses_column)
        bonuses_matches = re.findall(bonuses_pattern, bonuses_column)
        bonuses_dict = {int(num): desc.strip() for num, desc, _ in bonuses_matches}
        # print(f"bonus dict is {bonuses_dict}")

        # get the pieces column and get all pieces
        pieces_column = columns[2]
        pieces = pieces_column.find_all("span", class_="item")
        set_num_pieces = len(pieces)
    
        for piece in pieces:
            link = piece.find("a")
            if not link:
                continue
    
            # get name
            artifact_name = link.get("title")

            # get url
            base_url = "https://genshin-impact.fandom.com"
            artifact_url = f"{base_url}{link.get('href')}"
    
            artifact_data.append({
                "name": artifact_name,
                "artifactURL": artifact_url,
                "artifactSet": artifact_set_name,
                "maxSetQuality": max_set_quality,
                "setBonuses": bonuses_dict,
                "setNumPieces": set_num_pieces,
            })
    
    # Export to JSON
    output_file = "artifact-data.json"
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(artifact_data, json_file, indent=4)
    print(f"Data successfully written to {output_file}")


def main():
    get_artifacts()

main()