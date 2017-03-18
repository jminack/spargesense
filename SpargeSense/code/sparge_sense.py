"""frequency analysis for sparge tube sensing"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as ms
ms.use('seaborn-muted')

import librosa
import librosa.display


class Sample:
	def __init__(self):
		self._histo = None
		self._mels = None
		self._peak_hz = None
		
	def from_file(self, file_path):
		self._name = os.path.basename(file_path)
		self._data, self._sr = librosa.load(file_path)
		self._data = librosa.core.to_mono(self._data)
		return self
		
	def from_data(self, name, raw_data, sample_rate):
		self._name = name
		self._data = raw_data
		self._sr = sample_rate
		return self
		
	def melspec(self):
		"""returns mel-scaled power (energy-squared) spectrogram"""
		if self._mels is None:
			self._mels = librosa.feature.melspectrogram(self._data, sr=self._sr, n_mels=128)
		return self._mels
		
	def histogram(self):
		"""returns a normalised histogram over 128 frequency bins"""
		if self._histo is None:
			agg_hist = [np.sum(x) for x in self.melspec()]
			# normalise the samples (peak = 1.0)
			max_amplitude = max(agg_hist)
			self._histo = [x/max_amplitude for x in agg_hist]
		return self._histo
		
	def name(self):
		return self._name
	
	def data(self):
		return self._data
	
	def sample_rate(self):
		return self._sr

	def peak_hz(self):
		if self._peak_hz is None:
			max = np.max(self.histogram())
			for i in range(len(self.histogram())):
				if self.histogram()[i] == max:
					self._peak_hz = hz(i)
					break
		return self._peak_hz

def load_wav(file_path):
	"""loads a .wav file, returns a Sample object"""
	return Sample().from_file(file_path)

# helper methods

def _tr(s):
	"""transpose a list of lists"""
	return list(map(list, zip(*s)))

def hz(bin):
	"""convert from bin (0-127) to Hz"""
	return int(pow(2,(bin+221.81)/26.0245))


