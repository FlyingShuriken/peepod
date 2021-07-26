import discord
from pytube import Playlist, YouTube
from pygame import mixer
import json
import os


class Songs:
    def __init__(self, playlist_name):
        self.status = None
        self.current_song_position = "1"
        with open("settings.json", "r") as sett:
            sett = json.load(sett)
            if playlist_name in list(sett["playlist"].keys()):
                self.playlist_url = sett["playlist"][playlist_name]
                self.download()
            else:
                self.video_url = playlist_name
                self.single_song()

    def single_song(self):
        yt = YouTube(self.video_url, on_complete_callback=self.play)
        yt.streams.filter(progressive=False, file_extension='wav')

    def download(self):
        plyt = Playlist(self.playlist_url)
        print(plyt.video_urls[int(self.current_song_position)-1])
        yt = YouTube("https://www.youtube.com/watch?v=y_oFumwbj3k", on_complete_callback=self.play)
        yt.streams.filter(progressive=False, file_extension='wav')
        # os.system(
        # f"youtube-dl -x --audio-format wav --playlist-items {self.current_song_position} {self.playlist_url}"
        # )

    def play(self, stream=None, path=None):
        mixer.init()
        mixer.music.load(f"songs/{stream.title}.wav")
        mixer.music.play()

    def pause(self):
        mixer.music.pause()

    def stop(self):
        mixer.music.stop()

    def resume(self):
        mixer.music.unpause()


start = Songs("deep")
input()
