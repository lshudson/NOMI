import pyaudio
from itertools import chain
import numpy as np
import pyautogui
import keyboard
import random
import time
from scipy.io import wavfile
import scipy
from numpy import arange, cumsum, sin, linspace
from numpy import pi
import pandas as pd
import os

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

class Theremin:
    """
    Makes a Theremin to use for fun music making!
    Implements both mouse (x,y) coordinate theremin (x -> amp and y -> freq)
    and EEG concentration level theremin (concentration-time -> amp and concentration-level -> freq)
    """

    def __init__(self):

        self.infodict = {
            'sine': {'RATE': 44100, 'CHUNK': 1024, 'PITCH': 442, 'tonerange': 2, 'period': 0.01, 'minamp': 0.1,
                     'amprange': 0.5},
            'trumpet    ': {'RATE': 44100, 'CHUNK': 1024, 'PITCH': 442, 'tonerange': 2, 'period': 1.5441269841269842,
                            'minamp': 0.1, 'amprange': 0.5}}
        self.instrument1 = 'sine'
        self.instrument2 = 'sine'
        self.RATE1 = self.infodict[self.instrument1]['RATE']  # Sampling frequency
        self.CHUNK1 = self.infodict[self.instrument1]['CHUNK']  # buffer
        self.PITCH1 = self.infodict[self.instrument1]['PITCH']  # pitch
        self.minfreq1 = self.infodict[self.instrument1]['PITCH'] / 2 * 2 ** (3 / 12)
        self.tonerange1 = self.infodict[self.instrument1]['tonerange']
        self.period1 = self.infodict[self.instrument1]['period']
        self.minamp1 = self.infodict[self.instrument1]['minamp']
        self.amprange1 = self.infodict[self.instrument1]['amprange']
        self.RATE2 = self.infodict[self.instrument2]['RATE']  # Sampling frequency
        self.CHUNK2 = self.infodict[self.instrument2]['CHUNK']  # buffer
        self.PITCH2 = self.infodict[self.instrument2]['PITCH']  # pitch
        self.minfreq2 = self.infodict[self.instrument2]['PITCH'] / 2 * 2 ** (3 / 12)
        self.tonerange2 = self.infodict[self.instrument2]['tonerange']
        self.period2 = self.infodict[self.instrument2]['period']
        self.minamp2 = self.infodict[self.instrument2]['minamp']
        self.amprange2 = self.infodict[self.instrument2]['amprange']

    def distance(self):
        """
        Gets the The x and y from the pyautogui library
        :return:
        """
        x, y = pyautogui.position()
        return x, y

    def play_wave(self, stream, samples):
        stream.write(samples.astype(np.float32).tostring())

    def tonemapping_eeg(self, freq_channel, freq_div=1/5):
        freq = abs(freq_channel) / freq_div
        return freq

    def ampmapping_eeg(self, amp_channel, minamp=0.1, amprange=0.5, amp_div=2000):
        amp = minamp + amprange * abs(amp_channel) / amp_div
        return amp

    def make_time_varying_sine(self, start_freq, end_freq, start_A, end_A, fs, sec, phaze_start):
        freqs = linspace(start_freq, end_freq, num=int(round(fs * sec)))
        A = linspace(start_A, end_A, num=int(round(fs * sec)))
        phazes_diff = 2. * pi * freqs / fs  # Amount of change in angular frequency
        phazes = cumsum(phazes_diff) + phaze_start  # phase
        phaze_last = phazes[-1]
        ret = A * sin(phazes)  # Sine wave synthesis
        return ret, phaze_last

    def varying_tone(self, wave_data, freq, amp, critfreq=800, freq_div=1.1):
        # recommended: set critfreq to (7*max_freq/8) from your freq value generator
        relfreq = freq / critfreq
        relfreq += ((1 - relfreq) / freq_div)
        rem = relfreq % 1
        df = pd.DataFrame({'randvals': np.random.rand(len(wave_data)), 'data': wave_data})
        df['newmask'] = df['randvals'] <= rem
        outdata = (df['data'][df['newmask']])
        return (amp * np.array(outdata), -1)

    def from_wavfile(self, fn, maxamp=0.3):  # .wav filename with appropiate path relative to module
        fs, wavdata = wavfile.read(fn)
        file_minamp = wavdata.min()
        file_maxamp = wavdata.max()
        fileabs_maxamp = max([abs(file_minamp), abs(file_maxamp)])
        mult = maxamp / fileabs_maxamp
        outwavdata = wavdata * mult
        return fs, outwavdata

    def play_eegaudio(self, datastream , numchannels=1, instruments=''):
        """
        Plays audio, from an eeg stream
        :return:
        """
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32,
                        channels=numchannels,
                        rate=self.RATE1,
                        frames_per_buffer=self.CHUNK1 * numchannels,
                        output=True)

        phaze = 0

        if numchannels == 1:
            instrument = self.instrument1
            freq_old = self.minfreq1
            amp_old = self.minamp1
            while True:
                for i in range(len(datastream)):
                    row = stream[i]
                    amp_new = stream[row[0]]
                    freq_new = stream[row[1]]
                    if instrument == 'sine':

                        tone1 = self.make_time_varying_sine(freq_old, freq_new, amp_old, amp_new,
                                                        self.infodict[instrument]['RATE'],
                                                        self.infodict[instrument]['period'], phaze)
                    else:
                        tone1 = self.varying_tone(self.infodict[instrument1]['data'], freq_new1, amp_new1)

                    print(stream, tone1[0])
                    self.play_wave(stream, tone1[0])
                    freq_old = freq_new
                    amp_old = amp_new
                    phaze = tone1[1]

        elif numchannels == 2:
            phaze1 = 0
            phaze2 = 0
            instrument1 = instruments[0]
            instrument2 = instruments[1]
            freq_old1 = self.minfreq1
            amp_old1 = self.minamp1
            freq_old2 = self.minfreq2
            amp_old2 = self.minamp2
            while True:
                for i in range(len(datastream)):
                    row = stream[i]
                    amp_new1 = stream[row[0]]
                    freq_new1 = stream[row[1]]
                    amp_new2 = stream[row[2]]
                    freq_new2 = stream[row[3]]
                    if instrument1 == 'sine':

                        tone1 = self.make_time_varying_sine(freq_old1, freq_new1, amp_old1, amp_new1,
                                                            self.infodict[instrument1]['RATE'],
                                                            self.infodict[instrument1]['period'], phaze1)
                    elif instrument1 == 'fiddle1':
                        tone1 = self.varying_tone(self.fiddle1_mod, freq_new1, amp_new1)
                    elif instrument1 == 'fiddle2':
                        tone1 = self.varying_tone(self.fiddle2_mod, freq_new1, amp_new1)
                    elif instrument1 == 'trumpet':
                        tone1 = self.varying_tone(self.trumpet_mod, freq_new1, amp_new1)
                    else:
                        tone1 = self.varying_tone(self.infodict[instrument1]['data'], freq_new1, amp_new1)

                    if instrument2 == 'sine':
                        tone2 = self.make_time_varying_sine(freq_old2, freq_new2, amp_old2, amp_new2,
                                                            self.infodict[instrument2]['RATE'],
                                                            self.infodict[instrument1]['period'], phaze2)
                    elif instrument2 == 'fiddle1':
                        tone2 = self.varying_tone(self.fiddle1_mod, freq_new2, amp_new2)
                    elif instrument2 == 'fiddle2':
                        tone2 = self.varying_tone(self.fiddle2_mod, freq_new2, amp_new2)
                    elif instrument1 == 'trumpet':
                        tone2 = self.varying_tone(self.trumpet_mod, freq_new2, amp_new2)
                    else:
                        tone2 = self.varying_tone(self.infodict[instrument2]['data'], freq_new2, amp_new2)

                    tone = list(chain.from_iterable(zip(tone1[0], tone2[0])))
                    self.play_wave(stream, tone)
                    freq_old1 = freq_new1
                    amp_old1 = amp_new1
                    freq_old2 = freq_new2
                    amp_old2 = amp_new2
                    phaze1 = tone1[1]
                    phaze2 = tone2[1]

    def tonemapping(self):
        freq = self.distance()[1]
        return freq

    def ampmapping(self, amp_div=2000):
        amp = self.minamp1 + self.amprange1 * self.distance()[0] / amp_div
        return amp

    def play_audio(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=self.RATE1,
                        frames_per_buffer=self.CHUNK1,
                        output=True)
        freq_old = self.minfreq1
        amp_old = self.minamp1
        phaze = 0
        instrument = self.instrument1

        while True:
            try:
                if keyboard.is_pressed('q'):
                    stream.close()
                    break  # finishing the loop
                else:
                    freq_new = self.tonemapping()
                    amp_new = self.ampmapping()
                    if instrument == 'sine':

                        tone = self.make_time_varying_sine(freq_old, freq_new, amp_old, amp_new,
                                                           self.infodict[instrument]['RATE'],
                                                           self.infodict[instrument]['period'],
                                                           phaze)
                    else:
                        tone = self.varying_tone(self.infodict[instrument]['data'], freq_new, amp_new,
                                                 self.infodict[instrument]['RATE'],
                                                 self.infodict[instrument]['period'])

                    self.play_wave(stream, tone[0])
                    freq_old = freq_new
                    amp_old = amp_new
                    phaze = tone[1]
            except:
                continue

    def setinstrument1(self, instrument):
        self.instrument1 = instrument

    def setinstrument2(self, instrument):
        self.instrument2 = instrument

    def new_instrument(self, fn, name=''):
        if name == '':
            name = fn.split('/')[-1].split('.')[0]
        sr, data = self.from_wavfile(fn, maxamp=0.3)
        period = len(data) / 44100
        outdict = {'RATE': 44100, 'CHUNK': 1024, 'PITCH': 442, 'tonerange': 2, 'period': period, 'minamp': 0.1,
                   'amprange': 0.5, 'data': data}
        self.infodict[name] = outdict
        return name, data, outdict

    def testInstrument(self):
        pass


if __name__ == "__main__":
    # RUN YOUR CODE HERE
    # Example theremin simulator run with custom instrument (trumpet)
    myTheremin = Theremin()
    myTheremin.new_instrument(f".{os.path.sep}music{os.path.sep}" + "trumpetg2.wav", name='trumpetg2')
    myTheremin.setinstrument1('trumpetg2')
    myTheremin.play_audio()

