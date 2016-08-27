#!/usr/bin/python

import pygame
import threading
import time
import signal
import sys
import urllib2
import traceback
import serial
import RPi.GPIO as GPIO
import Adafruit_MCP3008

from dropbox_sync import MusicBoxSyncer
from player import MusicPlayer
from cloud_lights import CloudLights

event_lock = threading.Lock()
event_condvar = threading.Condition()
exit_flag = threading.Event()

has_new_files = True
was_button_pressed = False
syncer_thread = None

player = MusicPlayer()

NUM_CLOUD_LIGHTS = 15
CLOUD_UPDATE_TIME = 0.1

INPUT_CHECK_TIME = 0.2
BUTTON_DEBOUNCE_TIME = 0.2
SONG_CACHE_SIZE = 4

PIN_BUTTON = 26
PIN_SWITCH_LEFT = 19
PIN_SWITCH_RIGHT = 13
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

def _makeSerialOrNone(shouldLogError):
    try:
        return serial.Serial("/dev/ttyACM0", 19200)
    except serial.serialutil.SerialException:
        if shouldLogError:
            traceback.print_exc()
        return None

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

    lastInputCheckTime = 0

    # setup objects and pygame
    syncer_thread = threading.Thread(target=sync_thread)
    syncer_thread.start()

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(3)

    song_channel = pygame.mixer.Channel(1)
    effects_channel = pygame.mixer.Channel(2)

    is_a = False
    volume_music = 1024
    volume_effects = 1024

    # cloud effects
    c = CloudLights(NUM_CLOUD_LIGHTS)
    ser = _makeSerialOrNone(True)

    lastCloudUpdateTime = 0

    while not exit_flag.wait(timeout=0.01):
        currTime = time.time()

        if currTime - lastInputCheckTime >= INPUT_CHECK_TIME:
            lastInputCheckTime = currTime

            move_to_next_song = False

            with event_lock:
                is_a = not GPIO.input(PIN_SWITCH_RIGHT)
                if was_button_pressed:
                    print "Button press activated with is_a = %s" % is_a
                    move_to_next_song = True
                    was_button_pressed = False

                new_volume_music = mcp.read_adc(VOLUME_MUSIC_CHANNEL)
                new_volume_effects = mcp.read_adc(VOLUME_EFFECTS_CHANNEL)

                if new_volume_music != volume_music:
                    volume_music = new_volume_music
                    print "Music volume changed to %s" % volume_music
                    pygame.mixer.music.set_volume(volume_music / 1024.0)

                if new_volume_effects != volume_effects:
                    volume_effects = new_volume_effects
                    effects_channel.set_volume(volume_effects / 1024.0)
                    print "Effects volume changed to %s" % volume_effects

                if has_new_files:
                    files = MusicBoxSyncer.get_local_music_files()
                    if files and len(files) == 2:
                        player.set_songs(files[0], files[1])
                        print "Loading new songs: %s" % files
                    else:
                        print "Loaded files, but the array doesn't have two top-level entries: %s" % files
                    has_new_files = False

            if move_to_next_song or not pygame.mixer.music.get_busy():
                next_song = player.pop_next_song(is_a)
                if next_song:
                    print "Moving to next song (%s) with is_a = %s" % (next_song, is_a)
                    pygame.mixer.music.load(next_song)
                    pygame.mixer.music.play()

            if currTime - lastCloudUpdateTime >= CLOUD_UPDATE_TIME:
                lastCloudUpdateTime = currTime

                if ser:
                    serString = c.getCloudLightSerialString()
                    try:
                        ser.write(serString)
                    except serial.serialutil.SerialException:
                        traceback.print_exc()
                        ser = None
                else:
                    ser = _makeSerialOrNone(False)

def signal_handler(signal, frame):
    print "Got CTRL-C, exiting"
    exit_flag.set()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()