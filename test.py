from SpargeSense.code import sparge_sense as ss
import pyaudio
import wave
import librosa
import librosa.display
from sys import byteorder
from array import array
from struct import pack
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as ms

THRESHOLD = 600
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
outputfileName = ""
#
# functions defined below
#

def listen():
	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

	frames = []
	num_silent = 0
	snd_started = False
	
	while 1:
		# little endian, signed short
		data = stream.read(CHUNK)
		snd_data = array('h', data)
		if byteorder == 'big':
			snd_data.byteswap()

		silent = is_silent(snd_data)

		if silent:
			if snd_started:
				num_silent += 1
				if num_silent > 130:
					break
		else:
			if not snd_started:
				print "Found Start"
				snd_started = True

		if snd_started:
			frames.append(data)

	print("Found End")

	stream.stop_stream()
	stream.close()
	p.terminate()
	global outputfileName
	wf = wave.open(outputfileName, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()

def play():
	global outputfileName;
	wf = wave.open(outputfileName, 'rb')

	p = pyaudio.PyAudio()

	stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
					channels=wf.getnchannels(),
					rate=wf.getframerate(),
					output=True)

	data = wf.readframes(CHUNK)

	while data != '':
		stream.write(data)
		data = wf.readframes(CHUNK)

	stream.stop_stream()
	stream.close()

	p.terminate()
	
silence_debounce = 0
abs_max = 0

def is_silent(snd_data):
	global silence_debounce
	global abs_max
	"Returns 'True' if below the 'silent' threshold"
	max_data = max(snd_data)
	if max_data > 32000:
		print "----> Saturating <------"
	if max_data > abs_max:
		abs_max = max_data
		
	#print max_data
	if max_data > THRESHOLD:
		silence_debounce += 1
	else:
		silence_debounce = 0
	return silence_debounce <= 2 

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def bar(y, n): # y = [v1, v2...]
	plt.subplot(2,1,n)
	x = range(len(y))
	plt.bar(x,y,1/1.5)
	plt.title(samples[sn])
	plt.tight_layout()

def plot_waveform(y, sr, n):
	plt.subplot(2,1,n)
	librosa.display.waveplot(y, sr=sr)
	plt.title(samples[sn])
	plt.tight_layout()



"""
main function
"""
print "Starting"

while 1:
	outputfileName = time.strftime("output_%Y%m%d-%H%M%S.wav")
	outputPlotName = time.strftime("output_%Y%m%d-%H%M%S_plot.png")
	abs_max = 0
	
	print "Starting Recording"
	listen()
	# show graph
	samples = [ss.load_wav(outputfileName)]

	plt.figure(figsize=(12,4))
	
	for sample in samples:
		y = sample.histogram()
		plt.subplot(3,1,1)		
		plt.bar(range(len(y)),y,1/1.5)
		plt.title(str(sample.peak_hz()))
		plt.subplot(3,1,2)
		#librosa.display.specshow(sample._absmels,sample.sample_rate(), x_axis="time", y_axis="hz")
		plt.imshow(sample._absmels)
		plt.subplot(3,1,3)
		librosa.display.waveplot(sample.data(),sample.sample_rate())
		
		with open("histogram.txt", "a") as histFile:
			histFile.write(outputfileName)
			histFile.write(",")
			histFile.write(str(sample.histogram()))
			histFile.write("\n")
		print(sample.name(), sample.peak_hz())

	fig = plt.gcf()
	plt.show()
	fig.savefig(outputPlotName)
	print ("Starting Playback : Max value = %d" % (abs_max));
	#play()
	