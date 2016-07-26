#!/usr/bin/python

import dropbox_sync

def main():
    syncer = dropbox_sync.MusicBoxSyncer()
    syncer.sync()

if __name__ == "__main__":
    main()