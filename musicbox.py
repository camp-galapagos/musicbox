#!/usr/bin/python

from dropbox_sync import MusicBoxSyncer
from player import MusicPlayer
import pygame
import threading
import time

event_lock = threading.Lock()
event_condvar = threading.Condition()
has_new_files = True
is_a = False
was_button_pressed = False

def sync_thread():
    global has_new_files

    syncer = MusicBoxSyncer()

    # TODO: maybe blink that LED when syncing?
    while True:
        try:
            if syncer.sync():
                with event_lock:
                    has_new_files = True
                    event_condvar.notifyAll()
            time.sleep(15 * 60)
        except:
            time.sleep(60)


def main():
    global has_new_files
    global is_a
    global was_button_pressed

    syncer_thread = threading.Thread(sync_thread)
    syncer_thread.start()

    player = MusicPlayer()

    pygame.init()
    pygame.mixer.init()

    local_is_a = False

    # TODO: set up callbacks on GPIO to set is_a and was_button_pressed

    while True:
        move_to_next_song = False

        with event_lock:
            local_is_a = is_a
            if was_button_pressed:
                move_to_next_song = True
                was_button_pressed = False

            # TODO: read the potentiometer
            if has_new_files:
                files = MusicBoxSyncer.get_local_music_files()
                player.set_songs(files[0], files[1])
                has_new_files = False

        if not pygame.mixer.music.get_busy() or move_to_next_song:
            next_song = player.next_song(local_is_a)
            if next_song:
                pygame.mixer.music.load(next_song)
                pygame.mixer.music.play()

        event_condvar.wait(timeout=0.5)

if __name__ == "__main__":
    main()