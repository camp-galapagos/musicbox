#!/bin/bash
set -e

cd "$(dirname "$0")"

sudo apt-get -y install python-setuptools build-essential git mercurial python-dev python-numpy python-opengl \
    libav-tools libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev \
    libsdl1.2-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    libtiff5-dev libx11-6 libx11-dev fluid-soundfont-gm timgm6mb-soundfont \
    xfonts-base xfonts-100dpi xfonts-75dpi xfonts-cyrillic fontconfig fonts-freefont-ttf

sudo easy_install pip
sudo pip install --upgrade virtualenv

virtualenv env
./env/bin/pip install -r requirements.txt
