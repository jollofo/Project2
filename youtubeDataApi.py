## Imports ##

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import urllib.parse as p
import re
import os
import pickle

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def youtube_auth():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "credentials.json"
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    return build(api_service_name, api_version, credentials=creds)

# authenticate to YouTube API
youtube = youtube_auth()

"""
'get' functions to get video/channel data
"""
# Video data #
def get_vid_id_by_url(url):
    parsed_url = p.urlparse(url)
    video_id = p.parse_qs(parsed_url.query).get("v")
    if video_id:
        return video_id[0]
    else:
        raise Exception(f"Wasn't able to parse video URL: {url}")

def get_vid_details(youtube, **kwargs):
    return youtube.videos().list(part="snippet, contentDetails, statistics",**kwargs).execute()

## Channel data ##
def get_channel_id_by_url(youtube, url):
    """
    Returns channel ID of a given `id` and `method`
    - `method` (str): can be 'c', 'channel', 'user'
    - `id` (str): if method is 'c', then `id` is display name
        if method is 'channel', then it's channel id
        if method is 'user', then it's username
    """
    method, id = parse_channel_url(url)
    if method == "channel":
        return id
    elif method == "user":
        response = get_channel_details(youtube, forUsername=id)
        items = response.get("items")
        if items:
            channel_id = items[0].get("id")
            return channel_id
        raise Exception(f"Cannot find ID:{id} with {method} method")

def get_channel_videos(youtube, **kwargs):
    return youtube.search().list(
        **kwargs
    ).execute()


def get_channel_details(youtube, **kwargs):
    return youtube.channels().list(
        part="statistics,snippet,contentDetails",
        **kwargs
    ).execute()

def parse_channel_url(url):
    """
    This function takes channel `url` to check whether it includes a
    channel ID, user ID or channel name
    """
    path = p.urlparse(url).path
    id = path.split("/")[-1]
    if "/c/" in path:
        return "c", id
    elif "/channel/" in path:
        return "channel", id
    elif "/user/" in path:
        return "user", id

## printing video info ##

def print_video_infos(video_response):
    items = video_response.get("items")[0]
    snippet = items["snippet"]
    content_details = items["contentDetails"]
    statistics = items["statistics"]
    channel_title = snippet["channelTitle"]
    title = snippet["title"]
    view_count = statistics["viewCount"]
    print(f"""\
    Title: {title}
    Channel Title: {channel_title}
    Number of views: {view_count}
    """)

def main():
    channel_url = input("Enter a channel url: ")
    # get the channel ID from the URL
    channel_id = get_channel_id_by_url(youtube, channel_url)
    # get the channel details
    response = get_channel_details(youtube, id=channel_id)
    # extract channel infos
    snippet = response["items"][0]["snippet"]
    statistics = response["items"][0]["statistics"]
    channel_title = snippet["title"]
    channel_view_count  = statistics["viewCount"]
    # the following is grabbing channel videos
    # number of pages you want to get
    n_pages = 2
    # counting number of videos grabbed
    n_videos = 0
    next_page_token = None
    for i in range(n_pages):
        params = {
            'part': 'snippet',
            'q': '',
            'channelId': channel_id,
            'type': 'video',
            'videoCategoryId': 20 
        }
        if next_page_token:
            params['pageToken'] = next_page_token
        res = get_channel_videos(youtube, **params)
        channel_videos = res.get("items")
        for video in channel_videos:
            n_videos += 1
            video_id = video["id"]["videoId"]
            # easily construct video URL by its ID
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_response = get_vid_details(youtube, id=video_id)
            print(f"================Video #{n_videos}================")
            # print the video details
            print_video_infos(video_response)
            print(f"Video URL: {video_url}")
            print("="*40)
        print("*"*100)
        # if there is a next page, then add it to our parameters
        # to proceed to the next page
        if "nextPageToken" in res:
            next_page_token = res["nextPageToken"]

if __name__ == "__main__":
    main()