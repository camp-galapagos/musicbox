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

    def ensure_upcoming_songs(self, num_to_ensure):
        for p in self.playlists:
            if len(p[0]) < num_to_ensure:
                random.shuffle(p[1])
                p[0].extend([p[1].pop(0) for _ in xrange(num_to_ensure) if p[1]])

    def get_songs_to_cache(self, cache_size):
        self.ensure_upcoming_songs(cache_size)

        ret = []
        for p in self.playlists:
            ret.extend(p[0][:cache_size])
        return ret

    def _get_curr_playlist(self, is_a):
        self.ensure_upcoming_songs(1)

        curr_playlist = self.playlists[0 if is_a else 1]
        if not curr_playlist[0]:
            # there are no songs in this playlist. return None instead of erroring out
            return None

        return curr_playlist

    def peek_next_song(self, is_a):
        curr_playlist = self._get_curr_playlist(is_a)
        if not curr_playlist or not curr_playlist[0]:
            return None
        return curr_playlist[0][0]

    def pop_next_song(self, is_a):
        curr_playlist = self._get_curr_playlist(is_a)
        if not curr_playlist or not curr_playlist[0]:
            return None

        next_song = curr_playlist[0].pop(0)
        curr_playlist[1].append(next_song)
        return next_song
