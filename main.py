import discord
from pytube import Playlist, YouTube
from pygame import mixer
import json
import ffmpeg
import time
import os
from discord_rpc import rpc


class Songs:
    def __init__(self, playlist_name):
        self.status = None
        self.current_song_position = "1"
        with open("settings.json", "r") as sett:
            sett = json.load(sett)
            self.client = sett["client_id"]
            if playlist_name in list(sett["playlist"].keys()):
                self.playlist_url = sett["playlist"][playlist_name]
                self.first_play()
            else:
                self.video_url = playlist_name
                self.single_song()

    def single_song(self):
        yt = YouTube(self.video_url, on_complete_callback=self.play)
        yt.streams.filter(progressive=False, file_extension='wav')

    def first_play(self):
        plyt = Playlist(self.playlist_url)
        yt = YouTube("", on_complete_callback=self.convert)
        self.author = yt.author
        yt.streams.filter(type="audio").first().download(output_path="songs")

    def convert(self, stream=None, path=None):
        base = ffmpeg.input(path)
        new_path = f"{path[:-4]}.wav"
        output = ffmpeg.output(base, filename=new_path, f="wav")
        ffmpeg.run(output)
        self.play(stream=stream, path=new_path)

    def play(self, stream=None, path=None):
        mixer.init()
        mixer.music.load(path)
        mixer.music.play()
        start = time.time() + 5
        duration = float(ffmpeg.probe(path)["format"]["duration"])
        rpc_obj = rpc.DiscordIpcClient.for_platform(self.client_id)
        start_time = time.mktime(time.localtime())
        while True:
            time.sleep(0.5)
            if time.time() > (start + duration):
                print("done")
                mixer.quit()
                time.sleep(1)
                os.remove(f"{path[:-4]}.mp4")
                os.remove(f"{path[:-4]}.wav")
            else:
                activity = {
                    "state": self.author,  # anything you like
                    "details": stream.title,  # anything you like
                    "timestamps": {
                        "start": start_time
                    },
                    "assets": {
                        "small_text": "is playing a song",  # anything you like
                        "small_image": "is_playing_a_song",  # must match the image key
                        "large_text": "PeePod",  # anything you like
                        "large_image": "peepoo_s_personal_ai"  # must match the image key
                    }
                }
                rpc_obj.set_activity(activity)

    def pause(self):
        mixer.music.pause()

    def stop(self):
        mixer.music.stop()

    def resume(self):
        mixer.music.unpause()


while True:
    Songs("deep")
input()
