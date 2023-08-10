#!/usr/bin/env python

import os, subprocess, random, sys, time
import tweepy, dotenv

scriptpath = os.path.dirname(os.path.abspath(__file__))

# load the keys and secrets from the .env file
dotenv.load_dotenv(os.path.join(scriptpath, '.env'))

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

Client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    bearer_token=BEARER_TOKEN
)

ClientAuth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(ClientAuth)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")
    sys.exit(1)

video_dir = "videos/"

tmpimg = "tmpimg.jpg"

def getVideo():
    # return a video path
    video = random.choice(os.listdir(video_dir))
    return scriptpath + "/" + video_dir + video, video.split(".")[0]

def getDuration(video):
    # return the duration of a video
    cmd = [
        "ffprobe",
        "-i", video,
        "-show_entries", "format=duration",
        "-v", "quiet",
        "-of", "csv=%s" % ("p=0")
    ]
    #print(" ".join(cmd))

    return float(subprocess.check_output(cmd))

def getRandomScreenshot(video, duration):
    # return a random screenshot from a video
    screenshot = random.uniform(0, duration)
    cmd = [
        "ffmpeg",
        "-ss", str(screenshot),
        "-i", video,
        "-vframes", "1",
        "-q:v", "2",
        tmpimg
    ]
    #print(" ".join(cmd))
    subprocess.check_output(cmd)
    return tmpimg

timer = 3600.0
# one hour max
maxTimer = 3600.0
while True:
    timer += 1.0
    # should post ss?
    if timer >= maxTimer:
        
        timer = 0.0
        video, videoName = getVideo()
        duration = getDuration(video)
        screenshot = getRandomScreenshot(video, duration)
        mediaID = api.media_upload(screenshot)
        Client.create_tweet(
            text = videoName,
            media_ids = [mediaID.media_id]
        )
        # delete the screenshot
        os.remove(screenshot)

    # sleep for 1 second
    time.sleep(1.0)