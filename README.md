# NOMI
Neurally Operated Musical Instrument

![image](/Users/leilahudson/Downloads/NOMI.png)

The Neurally Operated Musical Instrument (NOMI) is a neurofeedback software which allows users to create music by altering and learning to control their brain state. NOMI comes with a GUI designed with QT designer and can be interfaced with a variety of headsets compatible with the Brainflow python package. The Brainflow python package also allows for simple implementations of sophisticated methods. NOMI consists of three core parts: a board communicator, a real-time EEG stream analyzer and a music generator. In order to ensure timely updates, the EEG stream is run on a separate thread than the music generation via python’s threading library. 

NOMI utilizes real-time EEG data to estimate the brain state of the user. NOMI currently supports two modes of operation: relaxation and concentration, each with their own assigned group of music channels. The user can also introduce their own .wav files for customized layering. The level of relaxation or concentration is currently determined using a pre-trained linear regression classifier, though other classifiers are also available via Brainflow. The prediction of the classifier is then mapped to thresholds of multiple music channels, where each channel has a different threshold. With increasing concentration (or relaxation), more channels are mixed and in a fully concentrated (or relaxed) state, all channels are mixed together. Pygame is used to mix and adjust the volume of the channels. 

More instructions to come later! 
The files you want to run will be located in the master_files directory.
Though there is some command-line compatibility, NOMI is designed to be used ideally with a gui, so run.py is what you'll want to use right now.

At the moment please run the file run.py and the GUI will appear.
