from pathlib import Path
import os
import pandas as pd
import pdb
import src.config as config
from scipy.io import wavfile

class AudioAnalyser:
    def __init__(self, folder, subjectId, sessionId) -> None:
        self.folder = folder
        self.audioFile = None
        self.eventsFile = None
        self.syubjectID = subjectId
        self.sessionId = sessionId
        self.loadAudioAndEvents()
        self.readAudio()
        self.readEvents()
        self.extractOvertEvents()

    def loadAudioAndEvents(self):
        files = os.listdir(self.folder)
        
        eventsFile = [file for file in files if file.endswith('.tsv')][0]
        audioFile = [file for file in files if file.endswith('.wav')][0]

        self.eventsFile = Path(self.folder, eventsFile)
        self.audioFile = Path(self.folder, audioFile)


    def readAudio(self):
        if self.audioFile:
            self.sampleRate, self.audio = wavfile.read(self.audioFile)

    def readEvents(self):

        if self.eventsFile:
            self.events = pd.read_csv(self.eventsFile, delimiter='\t')



    def extractOvertEvents(self):
        print('************************Extracting Audio****************')
        destination = Path(Path(Path(config.currDir,'Audios'),self.syubjectID), self.sessionId)
        os.makedirs(destination, exist_ok=True)

        overt = self.events[self.events['block']=='Overt']
        overt = overt[overt['trialType'] == 'StartSaying']
        overt.reset_index(inplace=True)

        for index in range(overt.shape[0]):
            
            start = overt['audioOnsetIndex'][index]
            word = overt['word'][index] 
            end = int(start + 1.5*self.sampleRate)

            audioSample = self.audio[start: end]
            audioName = Path(destination, f'{start}_{word}.wav')

            wavfile.write(audioName, self.sampleRate, audioSample)
            
            