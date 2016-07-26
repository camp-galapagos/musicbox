#!/usr/bin/python

import dropbox_sync

def main():
    syncer = dropbox_sync.MusicBoxSyncer()
    syncer.sync()

    files = syncer.get_local_music_files()

if __name__ == "__main__":
    main()