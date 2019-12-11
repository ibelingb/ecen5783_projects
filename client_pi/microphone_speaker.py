#!/usr/bin/python3
#
# ECEN5783
# Author: Brian Ibeling
# 11/14/2019

""" microphone_speaker.py: This file provides the microphone and speaker functionality for the Magic Wand
                           SuperProject. Also has ZMQ socket interfaces to send recorded audio filenames to
                           the client_pi process, and to output speaker audio received from client_pi.

+ Resources and Citations +
The following resources were used to assist with development of this SW.
  - https://makersportal.com/blog/2018/8/23/recording-audio-on-the-raspberry-pi-with-python-and-a-usb-microphone
  - http://wiki.sunfounder.cc/index.php?title=To_use_USB_mini_microphone_on_Raspbian
  - https://forum.core-electronics.com.au/t/awful-sound-to-noise-ratio-with-mini-usb-microphone/4079
"""
import sys
import time
import pyaudio
import wave
import zmq
from datetime import datetime
from pygame import mixer

__author__ = "Brian Ibeling"

FORM_1 = pyaudio.paInt16 # 16-bit resolution
CHANNELS = 1 # 1 channel
SAMPLE_RATE = 44100 # 48kHz sampling rate
BUFFER_FRAMES = 4096 # 2^12 samples for buffer
RECORD_SEC = 10 # seconds to record
DEVICE_INDEX = 2 # device index found by p.get_device_info_by_index(ii)

OUTPUT_AUDIO_DIR = "/home/pi/repos/ecen5783_project/client_pi/output_audio/"

# Define ZMQ socket for sending recorded audio filenames to client_pi
context = zmq.Context()
recordSocket = context.socket(zmq.PUB)
recordSocket.bind("tcp://127.0.0.1:6001")
speakerSocket = context.socket(zmq.SUB)
speakerSocket.setsockopt_string(zmq.SUBSCRIBE, "speak")
speakerSocket.connect("tcp://127.0.0.1:6004")

#-----------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------
# Object Instances and Variables
#-----------------------------------------------------------------------
def RecordAudio():
  audio = pyaudio.PyAudio() # create pyaudio instantiation
  outputAudioFile = "recordedAudio_" + str(datetime.now().strftime("%m%d%Y-%H%M%S")) + ".wav"
    
  # create pyaudio stream
  stream = audio.open(format = FORM_1,rate = SAMPLE_RATE,channels = CHANNELS, \
                      input_device_index = DEVICE_INDEX,input = True, \
                      frames_per_buffer=BUFFER_FRAMES)
  frames = []

  # loop through stream and append audio chunks to frame array
  for ii in range(0,int((SAMPLE_RATE/BUFFER_FRAMES)*RECORD_SEC)):
    data = stream.read(BUFFER_FRAMES, exception_on_overflow = False)
    frames.append(data)

  # stop the stream, close it, and terminate the pyaudio instantiation
  stream.stop_stream()
  stream.close()
  audio.terminate()

  # save the audio frames as .wav file
  wavefile = wave.open("audio_files/" + outputAudioFile,'wb')
  wavefile.setnchannels(CHANNELS)
  wavefile.setsampwidth(audio.get_sample_size(FORM_1))
  wavefile.setframerate(SAMPLE_RATE)
  wavefile.writeframes(b''.join(frames))
  wavefile.close()

  return outputAudioFile

#-----------------------------------------------------------------------
""" Main for Client_Pi Microphone process - 
TOOD
"""
def main(args):
  global recordSocket

  while True:
    # Capture audio via microphone, write to .wav file on RPi
    audioFilename = RecordAudio()

    # Write to msgQueue to client_pi to process recorded audio via AWS
    recordSocket.send_string(audioFilename)

    # Output speaker audio if signal received from client_pi
    try:
      # Receive signal from client_pi process to output audio
      outputAudio = speakerSocket.recv_string(flags=zmq.NOBLOCK)

      if(outputAudio == "speak"):
        print("Output Audio signal received")

        # Initialize Speaker
        mixer.init() #turn all of pygame on.

        # Output audio
        sound = mixer.music.load(OUTPUT_AUDIO_DIR + 'sound.mp3')
        sound = mixer.music.play()
        time.sleep(3) # Delay while audio file is played
        sound = mixer.music.stop()

        # Clear flag
        outputAudio = ""

        # Disable Speaker
        mixer.quit()

    except zmq.Again as e:
      # speaker signal not received
      outputAudio = ""

  return 0

if __name__ == '__main__':
  sys.exit(main(sys.argv))
