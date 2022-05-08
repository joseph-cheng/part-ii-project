import scipy.io.wavfile
import numpy as np

mono_data = np.array([0, 250, 500])

stereo_data = np.array([[0, 0], [250, -250], [500, -500]])

scipy.io.wavfile.write("3samples.wav", 44100, mono_data)
scipy.io.wavfile.write("3samples_stereo.wav", 44100, stereo_data)
