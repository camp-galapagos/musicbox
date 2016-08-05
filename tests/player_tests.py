#!/usr/bin/python

import unittest
import mock
import random

from player import MusicPlayer

class PlayerTests(unittest.TestCase):
    def setUp(self):
        self.player = MusicPlayer()

        # mock shuffle so it doesn't do anything
        self.shuffle_patcher = mock.patch("random.shuffle")
        self.shuffle_mock = self.shuffle_patcher.start()

    def tearDown(self):
        self.shuffle_patcher.stop()

    def assertSongsAre(self, is_a, song_list):
        expected_song_set = set(song_list)
        actual_song_set = set()

        for _ in xrange(len(song_list)):
            actual_song_set.add(self.player.next_song(is_a))

        self.assertEquals(expected_song_set, actual_song_set)

    def testInitialA(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])
        self.assertSongsAre(True, [1, 2, 3])
        self.shuffle_mock.assert_called()

    def testInitialB(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])
        self.assertSongsAre(False, ["A", "B", "C"])
        self.shuffle_mock.assert_called()

    def testRunOutOfSongsA(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])
        self.assertSongsAre(True, [1, 2, 3])

        self.assertSongsAre(True, [1, 2, 3])

    def testRunOutOfSongsB(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])

        self.assertSongsAre(False, ["A", "B", "C"])
        self.assertSongsAre(False, ["A", "B", "C"])

    def testAFullThenB(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])
        self.assertSongsAre(True, [1, 2, 3])
        self.assertSongsAre(False, ["A", "B", "C"])

    def testAPartialThenB(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])

        self.assertSongsAre(True, [1, 2])
        self.assertSongsAre(False, ["A", "C"])

    def testBPartialThenARunOut(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])

        self.assertSongsAre(False, ["A", "C"])
        self.assertSongsAre(True, [1, 2, 3])
        self.assertSongsAre(True, [1, 2, 3])

    def testCacheNormal(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])
        self.assertEquals(set(["A", "B", "C", 1, 2, 3]), set(self.player.get_songs_to_cache(3)))

    def testCacheTooMany(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])
        self.assertEquals(set(["A", "B", "C", 1, 2, 3]), set(self.player.get_songs_to_cache(25)))

    def testCacheAfterFinished(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])
        for i in xrange(2):
            self.player.next_song(True)
        self.assertEquals(set(["A", "B", "C", 1, 2, 3]), set(self.player.get_songs_to_cache(3)))

    def testEmpty(self):
        self.assertIsNone(self.player.next_song(True))
        self.assertIsNone(self.player.next_song(False))

        self.player.set_songs([], [])

        self.assertIsNone(self.player.next_song(True))
        self.assertIsNone(self.player.next_song(False))
