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

    def testInitialA(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])
        self.assertEquals(self.player.next_song(True), 1)
        self.assertEquals(self.player.next_song(True), 2)
        self.assertEquals(self.player.next_song(True), 3)

        self.assertEqual(1, len(self.shuffle_mock.mock_calls))

    def testInitialB(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])
        self.assertEquals(self.player.next_song(False), "A")
        self.assertEquals(self.player.next_song(False), "B")
        self.assertEquals(self.player.next_song(False), "C")

        self.assertEqual(1, len(self.shuffle_mock.mock_calls))

    def testRunOutOfSongsA(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])
        self.assertEquals(self.player.next_song(True), 1)
        self.assertEquals(self.player.next_song(True), 2)
        self.assertEquals(self.player.next_song(True), 3)
        self.assertEqual(1, len(self.shuffle_mock.mock_calls))

        self.assertEquals(self.player.next_song(True), 1)
        self.assertEquals(self.player.next_song(True), 2)
        self.assertEquals(self.player.next_song(True), 3)
        self.assertEqual(2, len(self.shuffle_mock.mock_calls))

    def testRunOutOfSongsB(self):
            self.player.set_songs([1, 2, 3], ["A", "B", "C"])
            self.assertEquals(self.player.next_song(False), "A")
            self.assertEquals(self.player.next_song(False), "B")
            self.assertEquals(self.player.next_song(False), "C")
            self.assertEqual(1, len(self.shuffle_mock.mock_calls))

            self.assertEquals(self.player.next_song(False), "A")
            self.assertEquals(self.player.next_song(False), "B")
            self.assertEquals(self.player.next_song(False), "C")
            self.assertEqual(2, len(self.shuffle_mock.mock_calls))

    def testAFullThenB(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])
        self.assertEquals(self.player.next_song(True), 1)
        self.assertEquals(self.player.next_song(True), 2)
        self.assertEquals(self.player.next_song(True), 3)

        self.assertEquals(self.player.next_song(False), "A")
        self.assertEquals(self.player.next_song(False), "B")
        self.assertEquals(self.player.next_song(False), "C")

    def testAPartialThenB(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])
        self.assertEquals(self.player.next_song(True), 1)
        self.assertEquals(self.player.next_song(True), 2)

        self.assertEquals(self.player.next_song(False), "A")
        self.assertEquals(self.player.next_song(False), "B")

    def testBPartialThenARunOut(self):
        self.player.set_songs([1, 2, 3], ["A", "B", "C"])

        self.assertEquals(self.player.next_song(False), "A")
        self.assertEquals(self.player.next_song(False), "B")

        self.assertEquals(self.player.next_song(True), 1)
        self.assertEquals(self.player.next_song(True), 2)
        self.assertEquals(self.player.next_song(True), 3)
        self.assertEquals(self.player.next_song(True), 1)

    def testEmpty(self):
        self.assertIsNone(self.player.next_song(True))
        self.assertIsNone(self.player.next_song(False))

        self.player.set_songs([], [])

        self.assertIsNone(self.player.next_song(True))
        self.assertIsNone(self.player.next_song(False))
