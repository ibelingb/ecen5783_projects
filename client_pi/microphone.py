#!/usr/bin/python3
#
# ECEN5783
# Author: Brian Ibeling
# 11/14/2019

""" microphone.py: 

+ Resources and Citations +
The following resources were used to assist with development of this SW.
  - https://makersportal.com/blog/2018/8/23/recording-audio-on-the-raspberry-pi-with-python-and-a-usb-microphone
  - http://wiki.sunfounder.cc/index.php?title=To_use_USB_mini_microphone_on_Raspbian
  - https://forum.core-electronics.com.au/t/awful-sound-to-noise-ratio-with-mini-usb-microphone/4079
"""
import sys
import pyaudio
import wave
from datetime import datetime

__author__ = "Brian Ibeling"

FORM_1 = pyaudio.paInt16 # 16-bit resolution
CHANNELS = 1 # 1 channel
SAMPLE_RATE = 44100 # 48kHz sampling rate
BUFFER_FRAMES = 4096 # 2^12 samples for buffer
RECORD_SEC = 3 # seconds to record
DEVICE_INDEX = 2 # device index found by p.get_device_info_by_index(ii)
MAX_RECORDINGS = 1 # Variable to track max number of recordings before ending program

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

  print("recording")
  frames = []

  # loop through stream and append audio chunks to frame array
  for ii in range(0,int((SAMPLE_RATE/BUFFER_FRAMES)*RECORD_SEC)):
    data = stream.read(BUFFER_FRAMES, exception_on_overflow = False)
    frames.append(data)

  print("finished recording")

  # stop the stream, close it, and terminate the pyaudio instantiation
  stream.stop_stream()
  stream.close()
  audio.terminate()

  # save the audio frames as .wav file
  wavefile = wave.open(outputAudioFile,'wb')
  wavefile.setnchannels(CHANNELS)
  wavefile.setsampwidth(audio.get_sample_size(FORM_1))
  wavefile.setframerate(SAMPLE_RATE)
  wavefile.writeframes(b''.join(frames))
  wavefile.close()

  return 0

#-----------------------------------------------------------------------
""" Main for Client_Pi Microphone process - 
TOOD
"""
def main(args):
  numRecordings = 0

  while numRecordings < MAX_RECORDINGS:
    # Capture audio via microphone, write to .wav file on RPi
    RecordAudio()

    # Send signal to client_pi process to send audio to AWS 
    # TODO

    numRecordings += 1

  return 0

if __name__ == '__main__':
  sys.exit(main(sys.argv))
