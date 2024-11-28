import requests
import json

def get_banners(base_url, limit=25, max_requests=2):
    '''
    ARGUMENTS:
        base_url: str representing GSHIMPACT API base url
        limit=25: int. the limit of how many responses are received per request. 25 by default.
        max_requests: int. the maximum number of requests to be made to the API
    
    RETURNS:
        None
    '''
    page = 1
    all_data = []
    for i in range(max_requests):
        resp = requests.get(f"{base_url}banners?limit={limit}&page={page}")
        # print(f"now getting data on page {page}")
        if resp.status_code != 200:
            print(f"Failed to get data: {resp.status_code}")
            return None

        # convert to json and add to all data
        data = resp.json()
        banners = data['results']
        all_data.append(banners)
        # print(f"{'-'*20}\ndata on page {page} is {data}\n\n{'-'*20}")

        # stop when the number of items is less than the limit
        # print(f"len data results is {len(data['results'])"}
        if len(data['results']) < limit:
            break
        page += 1

    # write to the file
    with open("banner-data.json", "w") as file:
        all_banners = [banner for page in all_data for banner in page]
        json.dump(all_banners, file, indent=4)



def main():
    get_banners(base_url="https://gsi.fly.dev/", limit=25, max_requests=2)

main()