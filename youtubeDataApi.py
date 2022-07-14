# Imports #
from googleapiclient.discovery import build

import os
import pickle
import urllib.parse as p
import sqlalchemy as db
import pandas as pd

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


# Video data #
def get_vid_id_by_url(url):
    parsed_url = p.urlparse(url)
    video_id = p.parse_qs(parsed_url.query).get("v")
    if video_id:
        return video_id[0]
    else:
        raise Exception(f"Wasn't able to parse video URL: {url}")


def get_vid_details(youtube, **kwargs):
    return youtube.videos().list(
        part="snippet, contentDetails, statistics",
        **kwargs
    ).execute()


# Channel data #
def get_channel_id_by_url(youtube, url):
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
    elif method == "c":
        response = youtube.search()
        items = response.get("items").list()
        if items:
            channel_id = items[0]["snippet"]["channelID"]
            return channel_id
    raise Exception(f"Cannot find ID:{id} with {method} method")


def get_channel_videos(youtube, **kwargs):
    return youtube.search().list(
        **kwargs
    ).execute()


def get_channel_details(youtube, **kwargs):
    return youtube.channels().list(
        part="statistics, snippet, contentDetails",
        **kwargs
    ).execute()


# Parsing the URL to get specific information
def parse_channel_url(url):
    path = p.urlparse(url).path
    id = path.split("/")[-1]
    if "/c/" in path:
        return "c", id
    elif "/channel/" in path:
        return "channel", id
    elif "/user/" in path:
        return "user", id


# printing video info #
def print_video_infos(video_response):
    items = video_response.get("items")[0]
    snippet = items["snippet"]
    statistics = items["statistics"]
    channel_title = snippet["channelTitle"]
    title = snippet["title"]
    publish_time  = snippet["publishedAt"]
    like_count = statistics["likeCount"]
    view_count = statistics["viewCount"]
    tags = snippet["tags"]
    print(f"""\
        Title: {title}
        Publish time: {publish_time}
        Number of views: {view_count}
        Number of likes: {like_count}
        Tags: {tags}
    """)


def youtube_main():
    channel_url = input("Enter a channel url: ")
    channel_id = get_channel_id_by_url(youtube, channel_url)
    response = get_channel_details(youtube, id=channel_id)
    snippet = response["items"][0]["snippet"]
    statistics = response["items"][0]["statistics"]
    channel_view_count  = statistics["viewCount"]
    n_pages = 2
    n_videos = 0
    next_page_token = None
    for i in range(n_pages):
        params = {
            'part': 'snippet',
            'q': '',
            'channelId': channel_id,
            'type': 'video',
        }
        res = get_channel_videos(youtube, **params)
        channel_videos = res.get("items")
        for video in channel_videos:
            n_videos += 1
            video_id = video["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_response = get_vid_details(youtube, id=video_id)
            print(f"================Video #{n_videos}================")
            print_video_infos(video_response)
            print(f"Video URL: {video_url}")
            print("="*40)
        
