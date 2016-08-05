#!/usr/bin/python

import random

class MusicPlayer(object):
    def __init__(self):
        self.playlists = [[[], []], [[], []]]

    def set_songs(self, a_songs, b_songs):
        new_songs = [a_songs, b_songs]

        # diff the song lists and add the new stuff to the played buffer
        for i in xrange(len(new_songs)):
            existing_songs = set([s for sublist in self.playlists[i] for s in sublist])
            added_songs = set(new_songs[i]) - set(existing_songs)
            self.playlists[i][1].extend(list(added_songs))

    def pop_next_song(self, is_a):
        curr_playlist = self.playlists[0 if is_a else 1]
        if not curr_playlist:
            return None

        if not curr_playlist[0]:
            if not curr_playlist[1]:
                return None
            random.shuffle(curr_playlist[1])
            curr_playlist[0] = curr_playlist[1]
            curr_playlist[1] = []

        next_song = curr_playlist[0].pop(0)
        curr_playlist[1].append(next_song)
        return next_song
