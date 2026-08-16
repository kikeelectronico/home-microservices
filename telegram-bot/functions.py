import os
import logging
import requests
from pytube import YouTube, Playlist

REQUEST_TIMEOUT = 10

def getPublicIP(endpoint):
    try:
        ip = requests.get(endpoint, timeout=REQUEST_TIMEOUT).text
        return ip
    except (requests.ConnectionError, requests.Timeout) as exception:
        logging.warning("Fail to get public IP. Error: %s", exception)
        return "Fail"

def getHomewareTest(api_url, api_key):
    try:
        url = api_url + "/api/devices/scene_dim/states"
        headers = {
            "Authorization": "bearer " + api_key
        }

        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            status = response.json()
            return "enable" in status
        else:
            return False
    except (requests.ConnectionError, requests.Timeout) as exception:
        logging.warning("Fail to get Homeware test. Error: %s", exception)
        return False

def test():
  return "I think this is broken. It has a hole."

def downloadYouTubeVideo(url, storage_client, bucket_name):
    try:
        if not 'list' in url:
            video = YouTube(url)
            video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
        else:
            playlist = Playlist(url)
            for video in playlist.videos:
                video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
    except Exception as exception:
        logging.warning("Fail to download YouTube video. Error: %s", exception)
        return []

    # Get the mp4 files
    all_in_dir = os.listdir('.')
    files = [something for something in all_in_dir if something.endswith('.mp4')]
    # Get the first file
    urls = []
    for file in files:
        try:
            # Upload to the bucket
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(file)
            blob.upload_from_filename(file)
            # Add URL
            urls.append("https://storage.cloud.google.com/" + bucket_name + "/" + file.replace(" ", "%20"))
        except Exception as exception:
            logging.warning("Fail to upload YouTube video to Google Storage. Error: %s", exception)
            continue

        try:
            # Delete the local file
            os.remove(file)
        except OSError as exception:
            logging.warning("Fail to delete local YouTube video. Error: %s", exception)
    # Return URL
    return urls
