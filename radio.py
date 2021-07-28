from pytube import Playlist, YouTube
from pygame import mixer
from random import shuffle
from json import load
import ffmpeg
from time import time, mktime, localtime, sleep
from os import remove
from discord_rpc import rpc


class Radio:
    def __init__(self, playlist_name):
        self.status = None
        self.current_song_position = "1"
        with open("settings.json", "r") as sett:
            sett = load(sett)
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
        self.plyt = Playlist(self.playlist_url)
        self.now = 0
        self.playlist = list(self.plyt.videos)
        shuffle(self.playlist)
        yt = self.playlist[self.now]
        yt.register_on_complete_callback(self.convert)
        self.author = yt.author
        yt.streams.filter(type="audio").first().download(output_path="songs")

    def after_play(self):
        yt = self.playlist[self.now]
        yt.register_on_complete_callback(self.convert)
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
        mixer.music.set_volume(0.05)
        mixer.music.play()
        start = mktime(localtime())
        duration = float(ffmpeg.probe(path)["format"]["duration"])
        self.rpc_obj = rpc.DiscordIpcClient.for_platform(self.client)
        end_time = int(round((mktime(localtime()) + duration),0))
        while True:
            sleep(0.5)
            if time() > end_time:
                self.stop(path=path)
            else:
                activity = {
                    "state": self.author,  # anything you like
                    "details": f"{stream.title.replace('/','')}",  # anything you like
                    "timestamps": {
                        "end": end_time
                    },
                    "assets": {
                        "small_text": "is playing a song",  # anything you like
                        "small_image": "is_playing_a_song",  # must match the image key
                        "large_text": "PeePod",  # anything you like
                        "large_image": "peepoo_s_personal_ai"  # must match the image key
                    }
                }
                self.rpc_obj.set_activity(activity)

    def pause(self):
        mixer.music.pause()

    def stop(self,path):
        mixer.quit()
        remove(f"{path[:-4]}.mp4")
        remove(f"{path[:-4]}.wav")
        self.now += 1
        self.rpc_obj.close()
        self.after_play()

    def resume(self):
        mixer.music.unpause()


Radio("i tot")
input()
