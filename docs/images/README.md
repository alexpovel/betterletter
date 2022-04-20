# Images

[GIF](demo.gif) generated using [ShareX](https://getsharex.com/)'s MP4 screen recording with [Carnac](https://github.com/Code52/carnac) to display live keystrokes on-screen.
Then:

```bash
# Create an initial fade-in from black. This is useful to demarcate the beginning for
# an infinitely looping GIF. From https://dev.to/dak425/add-fade-in-and-fade-out-effects-with-ffmpeg-2bj7
ffmpeg -i recording.mp4 -vf "fade=t=in:st=0:d=1" 01-faded.mp4
# Stopping the ShareX recording with `CTRL + SHIFT + PrtScreen` will show as a keystroke
# in Carnac. Hence, cut this last bit out and only use first couple seconds.
# First, the initial duration has be found out manually (we can't directly cut the last
# x.y seconds).
# https://ffmpeg.org/ffmpeg.html#Main-options
ffmpeg -i 01-faded.mp4 -t 3.400 02-cropped.mp4
# Freeze the last frame for a while before looping back to the beginning. This allows
# us to actually take in the final result for a short while.
# https://ffmpeg.org/ffmpeg-filters.html#tpad
ffmpeg -i 02-cropped.mp4 -vf "tpad=stop_mode=clone:stop_duration=2" 03-frozen.mp4
# Lastly, convert MP4 to GIF using some StackExchange black magick. Simply uploading to
# an online service might yield better results but wouldn't be reproducible.
# https://superuser.com/a/556031/1144470
ffmpeg -i 03-frozen.mp4 -vf "fps=10,scale=1024:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 demo.gif
```
