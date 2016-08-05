#!/usr/bin/python

import sys
import os
import subprocess

def main():
    if len(sys.argv) != 2:
        print "Requires one argument: the root directory of mp3 files to convert"
        sys.exit(1)

    for curr_dir, _, files in os.walk(sys.argv[1]):
        for f in files:
            if f.endswith(".mp3"):
                ogg_path = "%s%s" % (f[:-len(".mp3")], ".ogg")
                if not os.path.exists(ogg_path):
                    subprocess.call([
                        "ffmpeg", "-i", os.path.join(curr_dir, f), "-c", "libvorbis", os.path.join(curr_dir, ogg_path)
                    ])

if __name__ == "__main__":
    main()