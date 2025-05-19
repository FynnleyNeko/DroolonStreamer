import FreeSimpleGUI as sg
import subprocess as sp
import numpy as np
import cv2
import time
import argparse
from windows_capture import WindowsCapture, Frame, InternalCaptureControl
from mjpeg_streamer import MjpegServer, Stream

# Initialize argument parser
desc = "This application captures the ASeeVR preview images and outputs them via a configurable MJPEG stream for use in ETVR or other external applications. Made by FynnleyNeko"
parser = argparse.ArgumentParser(description = desc)
parser.add_argument("-a", "--address", default="127.0.0.1", metavar = "127.0.0.1", type = str, help = "Set the listening address of the MJPEG server / stream.")
parser.add_argument("-p", "--port", default=8080, choices = np.arange(1024, 65536, 1), metavar = "[1024-65536] (Default: 8080)", type = int, help = "Set the port of the MJPEG server / stream.")
parser.add_argument("-f", "--framerate", default=120, choices = np.arange(30, 121, 1), metavar = "[30-120] (Default: 120)", type = int, help = "Set the output framerate of the stream (not the capture framerate, this will always be your monitor refresh rate to ensure low latency).")
parser.add_argument("-q", "--quality", default=90, choices = np.arange(10, 101, 1), metavar = "[10-100] (Default: 90)", type = int, help = "Set the JPEG output quality of the stream, lower this if you need the stream externally and run into bandwidth limitations. Should never cause issues locally.")
parser.add_argument("-l", "--left_gamma", default=1.0, choices = np.around(np.arange(0.50, 2.01, 0.01), decimals=2), metavar = "[0.50-2.00] (Default: 1.0)", type = float, help = "Adjust the gamma (brightness curve) of the left camera. If your cameras are very contrasty this can in some cases make ETVR happier, but this is a LAST RESORT option, as it can raise the black value of your pupil and make stuff perform A LOT worse too.")
parser.add_argument("-r", "--right_gamma", default=1.0, choices = np.around(np.arange(0.50, 2.01, 0.01), decimals=2), metavar = "[0.50-2.00] (Default: 1.0)", type = float, help = "Adjust the gamma (brightness curve) of the right camera. If your cameras are very contrasty this can in some cases make ETVR happier, but this is a LAST RESORT option, as it can raise the black value of your pupil and make stuff perform A LOT worse too.")
args = parser.parse_args()

# Initialize variables
sg.theme('SystemDefault')
pimaxico = b'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'
windowmain = sg.Window('Droolon Streamer', icon=pimaxico)
leftEyeFrame = 0
rightEyeFrame = 0
leftEyeStart = time.time()
rightEyeStart = time.time()
leftEyeLastTry = time.time()
rightEyeLastTry = time.time()
leftEyeActive = False
rightEyeActive = False

# Build LUTs based on gamma adjustment
invLeftGamma = 1.0 / args.left_gamma
leftLUT = np.array([((i / 255.0) ** invLeftGamma) * 255
	for i in np.arange(0, 256)]).astype("uint8")
invRightGamma = 1.0 / args.right_gamma
rightLUT = np.array([((i / 255.0) ** invRightGamma) * 255
	for i in np.arange(0, 256)]).astype("uint8")


# Set up camera capture / input
leftEyeCapture = WindowsCapture(
    cursor_capture=False,
    draw_border=None,
    monitor_index=None,
    window_name="draw Image1",
)
rightEyeCapture = WindowsCapture(
    cursor_capture=False,
    draw_border=None,
    monitor_index=None,
    window_name="draw Image2",
)

# Set up webcam stream subprocesses / output
server = MjpegServer(args.address, args.port)
leftStream = Stream("left", size=(320, 240), quality=args.quality, fps=args.framerate)
rightStream = Stream("right", size=(320, 240), quality=args.quality, fps=args.framerate)
server.add_stream(leftStream)
server.add_stream(rightStream)
server.start()

# Make the capture threads able to change text in the main thread
def updateStatus(key, status, color):
    windowmain[key].update(status, text_color=color)

# Left capture thread
@leftEyeCapture.event
def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
    global leftEyeFrame, leftEyeStart

    # FPS calulation
    leftEyeFrame += 1
    if time.time() - leftEyeStart >= 1:
        updateStatus("-LEFTSTATUS-", str(leftEyeFrame-1) + " FPS", "green")
        leftEyeFrame = 0
        leftEyeStart = time.time()

    try:
        # Crop out the window border and throw out the alpha channel
        final = frame.crop(2,frame.height-241,322,frame.height-1).convert_to_bgr()

        # If there is a gamma adjustment, apply it via cv2.LUT, seems to be the cheapest way
        if args.left_gamma != 1.0:
            final.frame_buffer = cv2.LUT(final.frame_buffer, leftLUT)

        # Write the final frame to the stream
        leftStream.set_frame(final.frame_buffer)
    except Exception as e:
        print(e)

@leftEyeCapture.event
def on_closed():
    global leftEyeActive
    leftEyeActive = False
    updateStatus("-LEFTSTATUS-", "Not Found", "red")

# Right capture thread
@rightEyeCapture.event
def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
    global rightEyeFrame, rightEyeStart

    # FPS calulation
    rightEyeFrame += 1
    if time.time() - rightEyeStart >= 1:
        updateStatus("-RIGHTSTATUS-", str(rightEyeFrame-1) + " FPS", "green")
        rightEyeFrame = 0
        rightEyeStart = time.time()

    try:
        # Crop out the window border and throw out the alpha channel
        final = frame.crop(2,frame.height-241,322,frame.height-1).convert_to_bgr()

        # If there is a gamma adjustment, apply it via cv2.LUT, seems to be the cheapest way
        if args.right_gamma != 1.0:
            final.frame_buffer = cv2.LUT(final.frame_buffer, rightLUT)

        # Write the final frame to the stream
        rightStream.set_frame(final.frame_buffer)
    except Exception as e:
        print(e)

@rightEyeCapture.event
def on_closed():
    global rightEyeActive
    rightEyeActive = False
    updateStatus("-RIGHTSTATUS-", "Not Found", "red")

def locateEyes():
    locateLeftEye()
    locateRightEye()

def locateLeftEye():
    global leftEyeLastTry, leftEyeActive
    if leftEyeActive == False and leftEyeLastTry+2 <= time.time():
        try:
            leftEyeCapture.start_free_threaded()
            leftEyeActive = True
            leftEyeLastTry = time.time()
            updateStatus("-LEFTSTATUS-", "Starting", "orange")
        except Exception as e:
            leftEyeActive = False
            leftEyeLastTry = time.time()
            updateStatus("-LEFTSTATUS-", "Not Found", "red")
            print(e)

def locateRightEye():
    global rightEyeLastTry, rightEyeActive
    if rightEyeActive == False and rightEyeLastTry+2 <= time.time():
        try:
            rightEyeCapture.start_free_threaded()
            rightEyeActive = True
            rightEyeLastTry = time.time()
            updateStatus("-RIGHTSTATUS-", "Starting", "orange")
        except Exception as e:
            updateStatus("-RIGHTSTATUS-", "Not Found", "red")
            rightEyeActive = False
            rightEyeLastTry = time.time()
            print(e)

def make_windowmain():
    layout = [[sg.Text("Output:",font=(None,12,"bold"))],
              [sg.Text("Address:"), sg.Input("http://" + args.address + ":" + str(args.port), disabled=True, size=(32,1))],
              [sg.Text("Quality: " + str(args.quality) + "% Framerate: " + str(args.framerate) + " FPS")],
              [sg.Text("Captures:",font=(None,12,"bold"))],
              [sg.Text("Left Eye (/left)", size=(18,1)), sg.StatusBar('Not Found', size=(15,1), text_color='red', key='-LEFTSTATUS-')],
              [sg.Text("Right Eye (/right)", size=(18,1)), sg.StatusBar('Not Found', size=(15,1), text_color='red', key='-RIGHTSTATUS-')],
             ]
    return sg.Window('Droolon Streamer', layout, icon=pimaxico, finalize=True)

def main():
    global windowmain
    windowmain = make_windowmain()
    windowmain.timer_start(1000, repeating=True) # This sends an event every second to trigger locateEyes() repeatedly. (Starts / recovers image forwarding)
    
    while True:
        window, event, values = sg.read_all_windows()
        
        locateEyes() # Look for the Droolon tracker
        
        if window == sg.WIN_CLOSED:
            break
        if event == sg.WIN_CLOSED or event == 'Exit':
            server.stop()
            windowmain.close()
        elif event == '-IN-':
            windowmain['-OUTPUT-'].update(values['-IN-'])

if __name__ == '__main__':
    main()