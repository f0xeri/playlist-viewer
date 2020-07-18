import json
import requests
from jinja2 import Template

youtube_api_key = ""
youtube_api_link = "https://www.googleapis.com/youtube/v3/"


def set_google_api_key(key):
    global youtube_api_key
    youtube_api_key = key


def get_videos_from_playlist(playlist_id):
    """
    :param playlist_id: id of required playlist
    :return: list of videoIds
    """
    # header for api request
    headers = {
        "part": "snippet",
        "maxResults": 50,
        "playlistId": playlist_id,
        "key": youtube_api_key
    }
    # getting result
    videos = requests.get(youtube_api_link + "playlistItems", headers)
    videos = json.loads(videos.text)
    next_page_token = None

    videos_res = videos

    # if we have more than 50 videos in playlist, we need to get nextPageToken and do more requests
    if "nextPageToken" in videos:
        next_page_token = videos["nextPageToken"]

    # appending info about videos until we got last page
    while next_page_token is not None:
        headers["pageToken"] = next_page_token
        videos = requests.get(youtube_api_link + "playlistItems", headers)
        videos = json.loads(videos.text)
        if "nextPageToken" in videos:
            next_page_token = videos["nextPageToken"]
        else:
            next_page_token = None
        videos_res["items"] += videos["items"]

    # return list of videoId
    videoId_list = []
    for item in videos_res["items"]:
        videoId_list.append(item["snippet"]["resourceId"]["videoId"])
    return videoId_list


def get_videos_page(playlist_id):
    """
    :param playlist_id: id of required playlist
    :return: html file with all videos from playlist
    """
    videos = get_videos_from_playlist(playlist_id)
    template = Template("<h1>Playlist</h1>"
                        "<style>"
                        ".grid-container {"
                        "display: grid;"
                        "grid-template-columns: 20% 20% 20% 20%;"
                        "padding: 5px;"
                        "}"
                        ".grid-item {"
                        "padding: 10px;"
                        "text-align: center;"
                        "}"
                        "</style>"
                        "{% for row in videos | batch(4) %}"
                        ""
                        "<div class='grid-container'>{% for col in row %}"
                        '<div class="grid-item"><p><iframe width="420" height="315" src="https://www.youtube.com/embed/{{ col }}"></iframe></p></div>'
                        "{% endfor %}</div>"
                        "{% endfor %}")
    with open("file.html", "w") as file:
        file.write(template.render(videos=videos))
    return file
