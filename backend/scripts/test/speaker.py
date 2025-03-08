"""Code for generating brown noise on the Raspberry Pi 5"""

import numpy as np
#import sounddevice as sd
#import soundfile as sf
from scipy.io import wavfile
from scipy.signal import resample
import pigpio
from time import sleep

AUDIO_FILE = "cats_test.wav" # Import selected audio file for transmission
PWM_PIN = 18
CARRIER_FREQ = 40000
SAMPLERATE = 40000

#def convert_wav(file):
#    data, samplerate = sf.read(AUDIO_FILE)
#    return sf.write("cats_wav_test.wav", data, 40000, subtype='PCM_16')

def load_audio(file):
    samplerate, audio = wavfile.read(file)
    
    # If audio file is stereo, converts to mono by averaging both channels
    if audio.ndim == 2:
        audio = np.mean(audio, axis=1)

    new_len = int(len(audio) * SAMPLERATE / samplerate)
    audio = resample(audio, new_len).astype(np.float32)
    
    # Normalize between -1 and 1
    audio = audio / np.max(np.abs(audio))
    return audio

def am_modulate(audio, carrier_freq, samplerate):
    t = np.linspace(0, len(audio) / samplerate, len(audio))
    carrier = np.sin(2 * np.pi * carrier_freq * t)
    return carrier * audio

audio = load_audio(AUDIO_FILE)
modulated = am_modulate(audio, CARRIER_FREQ, SAMPLERATE)
modulated = (modulated + 1) / 2

pi = pigpio.pi('soft', 8888)

# Added in case pigpio decides to act
if not pi.connected():
    print("pigpio failed to connect!")
    exit()

pi.hardware_PWM(PWM_PIN, SAMPLERATE, 500000)

try:
    print("Directional Audio Laser ON")
    for sample in modulated:
        pwm_value = int(sample * 1000000)  # Convert to pigpio range (0 - 1M)
        pi.hardware_PWM(PWM_PIN, CARRIER_FREQ, pwm_value)
        sleep(1 / SAMPLERATE)
except KeyboardInterrupt:
    print("Stopping laser")
    pi.hardware_PWM(PWM_PIN, 0, 0)
    pi.stop()
