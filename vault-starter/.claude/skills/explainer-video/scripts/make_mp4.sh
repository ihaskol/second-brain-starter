#!/bin/bash
# Encode frames + mixed audio into an MP4 (H.264 + AAC, web-ready).
#   make_mp4.sh <framesdir> <fps> <audio.m4a> <out.mp4> [cover.jpg] [cover_seconds=1.5]
# A cover matters for slides: Keynote and PowerPoint show a video's first frame on the slide. With a cover,
# the audio is delayed by the same amount (shift caption times too).
set -euo pipefail
FR="$1"; FPS="$2"; AU="$3"; OUT="$4"; COVER="${5:-}"; CS="${6:-1.5}"
if [ -n "$COVER" ]; then
  MS=$(python3 -c "print(int(float('$CS')*1000))")
  ffmpeg -loglevel error -y -loop 1 -framerate "$FPS" -t "$CS" -i "$COVER" -framerate "$FPS" -i "$FR/%05d.jpg" -i "$AU" \
    -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0,format=yuv420p[v];[2:a]adelay=$MS|$MS[a]" -map "[v]" -map "[a]" \
    -c:v libx264 -crf 20 -preset medium -c:a aac -b:a 192k -movflags +faststart "$OUT"
else
  ffmpeg -loglevel error -y -framerate "$FPS" -i "$FR/%05d.jpg" -i "$AU" -c:v libx264 -pix_fmt yuv420p -crf 20 -preset medium \
    -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"
fi
# web copy for an artifact (seekable only when fetched as a Blob; see course-hub-builder):
#   ffmpeg -i out.mp4 -vf scale=-2:540 -crf 24 -c:a aac -b:a 128k -movflags +faststart out-540p.mp4
echo "wrote $OUT"
