import requests
import pandas
import json
import sqlalchemy as db

bearer_token = "AAAAAAAAAAAAAAAAAAAAAKoiegEAAAAA0IZDCXbvA8NvdTYghlfQ9iHi94U%3DV9Rg7pQVm9zitdrAU5YxRGKyrRbfR58m0bBhrfmj1BK9fvpXdK"
search_url = "https://api.twitter.com/2/tweets/counts/recent"


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentTweetCountsPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.request("GET", search_url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def twitter_main():
    game = input("Enter the name of a game: ")
    query_params = {'query': '#' + game + ' -is:retweet','granularity': 'day'}
    json_response = connect_to_endpoint(search_url, query_params)
    data = json_response["data"]
    for d in data:
      d["game"] = game
    df = pandas.DataFrame.from_dict(data)
    engine = db.create_engine('sqlite:///twitterdata.db')
    df.to_sql('Twitter', con=engine, if_exists='replace', index=False)
    query_result = engine.execute("SELECT * FROM Twitter;").fetchall()
    
    return pandas.DataFrame(query_result)
