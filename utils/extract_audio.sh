#!/bin/bash

yt-dlp -a "../data/yt_links.txt" -i -x --audio-format mp3 -o "../data/audio/%(id)s.mp3"