import src.config as config
from src.utils import loadXdfFile
from src.utils import adjustAudioTime
import pdb

class AudioData:
    def __init__(self, filepath):
        self.rawData = loadXdfFile(filepath)
        self.setupEegDataInfo()

    
    def setupEegDataInfo(self):
        
        """
        Load audio data from XDF file and initialize relevant attributes.
        """
        print('***************************Loading Audio data***************************')
        
        self.samplingFrequency = self.rawData[0][1]['info']['effective_srate']
        self.markers = self.rawData[0][0]['time_series']
        self.markersTimeStamps = adjustAudioTime(self.rawData[0][0]['time_stamps'])
        self.markersStartTime = self.markersTimeStamps[0]
        self.markersEndTime = self.markersTimeStamps[-1]

        self.audio = self.rawData[0][1]['time_series']
        self.audioTimeStamps = adjustAudioTime(self.rawData[0][1]['time_stamps'])
        self.audioStartTime = self.audioTimeStamps[0]
        self.audioEndTime = self.audioTimeStamps[-1]

        self.nMarkers = len(self.markers)
        