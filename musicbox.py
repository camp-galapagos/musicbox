#!/usr/bin/python

from dropbox_sync import MusicBoxSyncer
from player import MusicPlayer

import pygame
import threading
import time
import signal
import sys
import urllib2
import traceback
import RPi.GPIO as GPIO
import Adafruit_MCP3008

event_lock = threading.Lock()
event_condvar = threading.Condition()
exit_flag = threading.Event()

has_new_files = True
was_button_pressed = False
syncer_thread = None

player = MusicPlayer()

BUTTON_DEBOUNCE_TIME = 0.2
SONG_CACHE_SIZE = 4

PIN_BUTTON = 26
PIN_SWITCH_LEFT = 13
PIN_SWITCH_RIGHT = 19
PIN_CLK = 21 # SCLK
PIN_CS  = 12 # CE0
PIN_MISO = 20 # DOUT
PIN_MOSI = 16 # DIN

VOLUME_MUSIC_CHANNEL = 0
VOLUME_EFFECTS_CHANNEL = 7

def sync_thread():
    global has_new_files

    syncer = MusicBoxSyncer()

    # TODO: maybe blink that LED when syncing?
    while True:
        try:
            if syncer.sync():
                with event_lock:
                    has_new_files = True
                    with event_condvar:
                        event_condvar.notifyAll()

            # if we didn't hit an exception, then we're connected to the internet. long timeout
            if exit_flag.wait(timeout=15.0 * 60):
                print "Syncer got exit flag -- exiting"
                return
        except urllib2.HTTPError:
            print "Syncer: not connected to the internet"
            if exit_flag.wait(60.0):
                print "Syncer got exit flag -- exiting"
                return
        except:
            traceback.print_exc("Syncer: unknown error")
            if exit_flag.wait(60.0):
                print "Syncer got exit flag -- exiting"
                return


last_button_press_time = 0

def button_pressed(channel):
    global was_button_pressed
    global last_button_press_time

    curr_time = time.time()

    if not GPIO.input(channel) and curr_time - last_button_press_time >= BUTTON_DEBOUNCE_TIME:
        last_button_press_time = curr_time
        with event_lock:
            print "Button was pressed!"
            was_button_pressed = True
            with event_condvar:
                event_condvar.notifyAll()

file_to_sound_cache = {}
new_song_condvar = threading.Condition()
player_lock = threading.Lock()

def prefetch_data():
    global player

    print "Starting prefetcher thread"

    prefetch_size = 1

    while not exit_flag.isSet():
        songs_to_have_in_cache = []
        songs_to_load = []

        with player_lock:
            songs_to_have_in_cache = player.get_songs_to_cache(prefetch_size)
            songs_to_load = [song for song in songs_to_have_in_cache if song not in file_to_sound_cache]

        did_prefetch = False

        if songs_to_load:
            print "Prefetching %s" % songs_to_load
            local_sound_cache = {}
            for song in songs_to_load:
                print "Pretching %s" % song
                local_sound_cache[song] = pygame.mixer.Sound(song)
                did_prefetch = True
            print "Prefetch complete"

            with player_lock:
                file_to_sound_cache.update(local_sound_cache)
                for song in file_to_sound_cache.iterkeys():
                    if song not in songs_to_have_in_cache:
                        del file_to_sound_cache[song]

        print "Prefetcher sleeping"
        if did_prefetch:
            prefetch_size = min(prefetch_size + 1, SONG_CACHE_SIZE)
        with new_song_condvar:
            new_song_condvar.wait(timeout=3)
        print "Prefetcher awake"

    print "Prefetcher got exit signal"

def main():
    global has_new_files
    global was_button_pressed

    # set up pins
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(PIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(PIN_BUTTON, GPIO.BOTH, callback=button_pressed, bouncetime=300)

    GPIO.setup(PIN_SWITCH_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PIN_SWITCH_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    mcp = Adafruit_MCP3008.MCP3008(clk=PIN_CLK, cs=PIN_CS, miso=PIN_MISO, mosi=PIN_MOSI)

    # setup objects and pygame
    syncer_thread = threading.Thread(target=sync_thread)
    syncer_thread.start()
    prefetcher_thread = threading.Thread(target=prefetch_data)
    prefetcher_thread.start()

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(3)

    song_channel = pygame.mixer.Channel(1)
    effects_channel = pygame.mixer.Channel(2)

    song_sound = None
    song_file = None

    is_a = False
    volume_music = 0
    volume_effects = 0

    while not exit_flag.wait(timeout=0.25):
        move_to_next_song = False

        with event_lock:
            is_a = GPIO.input(PIN_SWITCH_LEFT)
            if was_button_pressed:
                print "Button press activated with is_a = %s" % is_a
                move_to_next_song = True
                was_button_pressed = False

            new_volume_music = mcp.read_adc(VOLUME_MUSIC_CHANNEL)
            new_volume_effects = mcp.read_adc(VOLUME_EFFECTS_CHANNEL)

            if new_volume_music != volume_music:
                volume_music = new_volume_music
                print "Music volume changed to %s" % volume_music
                song_channel.set_volume(volume_music / 1024.0)

            if new_volume_effects != volume_effects:
                volume_effects = new_volume_effects
                effects_channel.set_volume(volume_effects / 1024.0)
                print "Effects volume changed to %s" % volume_effects

            if has_new_files:
                files = MusicBoxSyncer.get_local_music_files()
                if files and len(files) == 2:
                    with player_lock:
                        player.set_songs(files[0], files[1])
                    print "Loading new songs: %s" % files
                else:
                    print "Loaded files, but the array doesn't have two top-level entries: %s" % files
                has_new_files = False

        if move_to_next_song or not song_channel.get_sound():
            with player_lock:
                next_song = player.peek_next_song(is_a)
                if next_song:
                    if next_song != song_file:
                        print "Moving to next song (%s) with is_a = %s" % (next_song, is_a)
                    song_sound = file_to_sound_cache.get(next_song)
                    if song_sound:
                        player.pop_next_song(is_a)
                        song_channel.play(song_sound)
                        print "Playing %s" % next_song
                        with new_song_condvar:
                            new_song_condvar.notifyAll()
                    else:
                        if next_song != song_file:
                            print "Tried to load %s but it wasn't in the cache!" % next_song
                    song_file = next_song

def signal_handler(signal, frame):
    print "Got CTRL-C, exiting"
    exit_flag.set()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()