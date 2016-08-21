#!/usr/bin/python

import sys
import os
import subprocess

def main():
    if len(sys.argv) != 3:
        print "args: [root dir of mp3s] [root directory of oggs]"
        sys.exit(1)

    mp3_dir = sys.argv[1]
    ogg_dir = sys.argv[2]

    for curr_dir, _, files in os.walk(mp3_dir):
        for f in files:
            if f.endswith(".mp3"):
                local_dir = curr_dir[len(mp3_dir)+1:]
                ogg_path = os.path.join(ogg_dir, local_dir, "%s%s" % (f[:-len(".mp3")], ".ogg"))
                if not os.path.exists(ogg_path):
                    subprocess.call([
                        "ffmpeg", "-i", os.path.join(curr_dir, f), "-c", "libvorbis", os.path.join(curr_dir, ogg_path)
                    ])

if __name__ == "__main__":
    main()