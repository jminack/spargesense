import sparge_sense as ss

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as ms
ms.use('seaborn-muted')

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

sample_root = '/Users/richard/Documents/code/hackathon/unearthed/'
files = ['FossilFoolsLong1.wav', 'FossilFoolsShort1.wav']

samples = []

for i in range(len(files)):
	samples.append(ss.load_wav(sample_root+files[i]))

fig, ax = plt.subplots()
plt.figure(figsize=(12,4))

for sample in samples:
	y = sample.histogram()
	ax.bar(range(len(y)),y,1/1.5)
	print(sample.name(), sample.peak_hz())

ax.set_xticklabels([str(ss.hz(x)) for x in range(0, 128,10)])

plt.show()

