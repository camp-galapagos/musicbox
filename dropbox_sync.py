#!/usr/bin/python

import dropbox
from secrets import DROPBOX_TOKEN
import os
import errno

DBX_MUSIC_PATH = u"/galapagos_music"

class MusicBoxSyncer(object):
    def __init__(self):
        self.dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    @classmethod
    def _get_or_create_music_dir(cls):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        music_dir = os.path.join(current_dir, "music")

        if not os.path.exists(music_dir):
            os.mkdir(music_dir)

        return music_dir

    @classmethod
    def get_local_music_files(cls):
        file_list = []

        music_dir = MusicBoxSyncer._get_or_create_music_dir()
        for _, dirs, _ in os.walk(music_dir):
            for d in dirs:
                files = []
                for curr_dir, _, files in os.walk(os.path.join(music_dir, d)):
                    files.extend([os.path.join(curr_dir, f) for f in files])
                file_list.append(files)
        return file_list

    # returns True if we downloaded new files, False otherwise
    def sync(self):
        print "Starting sync..."

        music_dir = self._get_or_create_music_dir()

        local_file_to_size = {}
        for curr_dir, dirs, files in os.walk(music_dir):
            for fname in files:
                local_file_path = os.path.join(curr_dir, fname)
                local_file_to_size[os.path.relpath(local_file_path, music_dir)] = os.path.getsize(local_file_path)

        has_synced_something = False
        folder_results = self.dbx.files_list_folder(DBX_MUSIC_PATH, recursive=True)
        for metadata in folder_results.entries:
            # strip the dbx music path from the beginning of the absolute dbx path, and a +1 to strip the /
            relative_path = metadata.path_display[len(DBX_MUSIC_PATH) + 1:]

            if isinstance(metadata, dropbox.files.FileMetadata) and (
                (relative_path not in local_file_to_size or metadata.size != local_file_to_size[relative_path])
            ):
                print "Syncing down %s " % relative_path

                md, res = self.dbx.files_download(metadata.path_lower)
                data = res.content

                # do a mkdir -p on the parent directory
                relative_dir = os.path.dirname(relative_path)
                if relative_dir[0] == "/":
                    relative_dir = relative_dir[1:]

                local_dir = os.path.join(music_dir, relative_dir)

                if not os.path.exists(local_dir):
                    try:
                        os.makedirs(local_dir)
                        print "\tCreated %s" % local_dir
                    except OSError as exc:
                        if exc.errno == errno.EEXIST and os.path.isdir(local_dir):
                            pass
                        else:
                            raise

                with open(os.path.join(music_dir, relative_path), "wb") as f:
                    f.write(data)
                    has_synced_something = True

        print "Syncing complete"
        return has_synced_something
