import requests
import json
bearer_token = "AAAAAAAAAAAAAAAAAAAAAKoiegEAAAAA0IZDCXbvA8NvdTYghlfQ9iHi94U%3DV9Rg7pQVm9zitdrAU5YxRGKyrRbfR58m0bBhrfmj1BK9fvpXdK"
search_url = "https://api.twitter.com/2/tweets/counts/recent"

# Optional params: start_time,end_time,since_id,until_id,next_token,granularity
query_params = {'query': '#pokemon -is:retweet','granularity': 'day'}

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentTweetCountsPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.request("GET", search_url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def main():
    json_response = connect_to_endpoint(search_url, query_params)
    print(json.dumps(json_response, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
