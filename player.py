#!/usr/bin/python

import random

class MusicPlayer(object):
    def __init__(self):
        self.a_songs = []
        self.b_songs = []
        self.curr_playlist = []
        self.is_a = False

    def set_songs(self, a_songs, b_songs):
        self.a_songs = a_songs
        self.b_songs = b_songs

    def next_song(self, is_a):
        # if we ran out of songs or we're switching playlists
        if not self.curr_playlist or self.is_a != is_a:
            self.is_a = is_a
            self.curr_playlist = list(self.a_songs if is_a else self.b_songs)
            random.shuffle(self.curr_playlist)

        if not self.curr_playlist:
            return None
        return self.curr_playlist.pop(0)

    def set_volume(self, volume):
        pass