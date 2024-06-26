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
tmpvid = "tmpvid.mp4"

max_attempts = 10
current_attempts = 0

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

def getRandomVideoClip(video, duration, clipLength):
    # clips vary from 5-15 seconds
    clipStart = random.uniform(0, duration - clipLength)
    cmd = [
        "ffmpeg",
        "-ss", str(clipStart),
        "-i", video,
        "-t", str(clipLength),
        "-c", "copy",
        tmpvid
    ]
    #print(" ".join(cmd))
    subprocess.check_output(cmd)
    return tmpvid

timer = 1800.0
# one hour max
maxTimer = 1800.0
while True:
    timer += 1.0
    # should post ss?
    if timer >= maxTimer:
        timer = 0.0
        video, videoName = getVideo()
        duration = getDuration(video)
        #50/50 chance for screenshot or video clip
        while True:
            try:
                screenshot = random.randint(0, 1) == 0 and getRandomScreenshot(video, duration) or getRandomVideoClip(video, duration, random.uniform(5.0, 15.0))
                mediaID = api.media_upload(screenshot)
                Client.create_tweet(
                    text = videoName,
                    media_ids = [mediaID.media_id]
                )
                break
            except Exception as e:
                print("Error: ", e)
                current_attempts += 1
                print("Attempt: ", current_attempts)
                if current_attempts == max_attempts:
                    print("Max attempts reached. Waiting for next tweet.")
                    break
                continue
        current_attempts = 0

                    
        # delete the screenshot
        os.remove(screenshot)

    # sleep for 1 second
    time.sleep(1.0)