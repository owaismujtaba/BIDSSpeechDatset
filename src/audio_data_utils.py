import src.config as config
from src.utils import loadXdfFile
from src.utils import adjustAudioTime
import pdb

class AudioDataProcessor:
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

    def cleanMarkers(self):
        markers = []
        start = None
        block = None
        event = None
        for i in range(len(self.markers)):
            marker = self.markers[i][0]
            if marker != 'StartBlockSaying' and start == None:
                start = 'done'
                continue

            if 'BlockSaying' in marker:
                block = 'Saying'
            if 'BlockThinking' in marker:
                block = 'Thinking'
            if 'EndReading' in marker:
                event = 'ITI'
            elif 'EndSaying' in marker:
                event = 'Fixation'
            else:
                event = marker
            
            markers.append([event, block, self.markersTimeStamps[i]])

        self.markersNew = markers