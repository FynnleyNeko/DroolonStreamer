# Fynnleys Droolon Streamer
![screenshot](https://github.com/user-attachments/assets/2022d825-85aa-48a3-86b7-a50434270516)

### Note
**[DroolonStreamer got a spiritual successor](https://github.com/FynnleyNeko/PiCamLite) called PiCamLite!** The new tool allows higher framerates in EyeTrackVR and fully replaces the aSeeVR runtime to save your CPU cycles by cutting out aSeeVRs tracking! And even better? *All that while being 13MB smaller than DroolonStreamer!*

# Usage

| Option | Range / Default | Description |
| --- | --- | --- |
| -a  / --address | 127.0.0.1 | Set the listening address of the MJPEG server / stream. |
| -p / --port | 1024-65536 (Default: 8080) | Set the port of the MJPEG server / stream. |
| -f / --framerate | 30-120 (Default: 120) | Set the output framerate of the stream (not the capture framerate, this will always be your monitor refresh rate to ensure low latency). |
| -q / --quality | 10-100 (Default: 90) | Set the JPEG output quality of the stream, lower this if you need the stream externally and run into bandwidth limitations. Should never cause issues locally. |
| -l / --left_gamma | 0.50-2.00 (Default: 1.0) | Adjust the gamma (brightness curve) of the left camera. If your cameras are very contrasty this can in some cases make ETVR happier, but this is a LAST RESORT option, as it can raise the black value of your pupil and make stuff perform A LOT worse too. |
| -r / --right_gamma | 0.50-2.00 (Default: 1.0) | Adjust the gamma (brightness curve) of the right camera. If your cameras are very contrasty this can in some cases make ETVR happier, but this is a LAST RESORT option, as it can raise the black value of your pupil and make stuff perform A LOT worse too. |

# Build

Build using nuitka with: 
```python -m nuitka --windows-console-mode=attach --enable-plugins=tk-inter --onefile --standalone droolonstreamer.py```
