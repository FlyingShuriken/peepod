from pytube import Playlist, YouTube
from pygame import mixer
from random import shuffle
from json import load
import ffmpeg
from time import mktime, localtime
from os import remove
from discord_rpc import rpc


class Radio:
    def __init__(self, playlist_name):
        self.status = ""
        self.current_song_position = "1"
        with open("settings.json", "r") as sett:
            sett = load(sett)
            self.client = sett["client_id"]
            if playlist_name in list(sett["playlist"].keys()):
                self.playlist_url = sett["playlist"][playlist_name]
                self.first_play()

    def single_song(self,link):
        yt = YouTube(link, on_complete_callback=self.convert)
        self.playlist.insert((self.now+1), yt)

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
        mixer.music.set_volume(0.2)
        mixer.music.play()
        start = mktime(localtime())
        duration = float(ffmpeg.probe(path)["format"]["duration"])
        self.rpc_obj = rpc.DiscordIpcClient.for_platform(self.client)
        self.end_time = int(round((mktime(localtime()) + duration),0))
        self.radio_path = path
        activity = {
            "state": self.author,
            "details": f"{stream.title.replace('/','')}",
            "timestamps": {
                "end": self.end_time
            },
            "assets": {
                "small_text": "is playing a song",
                "small_image": "is_playing_a_song",
                "large_text": "PeePod",
                "large_image": "peepoo_s_personal_ai"
            },
            "buttons": [{"label":"View This Project on Github","url":"https://github.com/FlyingShuriken/peepod"}]
        }
        self.rpc_obj.set_activity(activity)

    def pause(self):
        mixer.music.pause()

    def continue_play(self):
        mixer.music.play()

    def stop(self,path,next_when_loop=None):
        if self.status == "loop":
            mixer.quit()
            remove(f"{path[:-4]}.mp4")
            remove(f"{path[:-4]}.wav")
            if next_when_loop:
                self.now += 1
            self.rpc_obj.close()
            if self.status != "stop":
                self.after_play()
        else:
            mixer.quit()
            remove(f"{path[:-4]}.mp4")
            remove(f"{path[:-4]}.wav")
            self.now += 1
            self.rpc_obj.close()
            if self.status != "stop":
                self.after_play()

    def resume(self):
        mixer.music.unpause()

    def next(self,path):
        self.stop(path,True)

    def previous(self,path):
        mixer.quit()
        remove(f"{path[:-4]}.mp4")
        remove(f"{path[:-4]}.wav")
        self.now -= 1
        self.rpc_obj.close()
        if self.status != "Stop":
            self.after_play()

    def shuffle(self):
        self.current_song_position = 0
        shuffle(self.playlist)

    def loop(self):
        self.status = "loop"

    def unloop(self):
        self.status = ""
