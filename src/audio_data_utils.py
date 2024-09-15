import src.config as config
from src.utils import loadXdfFile
from src.utils import adjustAudioTime, findNearestIndices
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
        self.markersTimeStamps = self.rawData[0][0]['time_stamps']
        self.markersStartTime = self.markersTimeStamps[0]
        self.markersEndTime = self.markersTimeStamps[-1]

        self.audio = self.rawData[0][1]['time_series']
        self.audioTimeStamps = self.rawData[0][1]['time_stamps']
        self.audioStartTime = self.audioTimeStamps[0]
        self.audioEndTime = self.audioTimeStamps[-1]
        self.nMarkers = len(self.markers)
        print('***************************Audio data loaded***************************')

        self.mapAudioEvents()

    def mapAudioEvents(self):
        print('***************************Mapping Audio events***************************')
        markersMappingIndexs = findNearestIndices(self.audioTimeStamps, self.markersTimeStamps)
        self.audioTimeStamps = adjustAudioTime(self.audioTimeStamps)
        events = []
        block = None
        for index in range(len(markersMappingIndexs)):
            marker = self.markers[index][0]
            if 'BlockSaying' in marker:
                block = 'Overt'
            if 'BlockThinking' in marker:
                block = 'Inert'
            if 'EndReading' in marker:
                event = 'ITI'
            elif 'EndSaying' in marker:
                event = 'Fixation'
            else:
                event = marker
            onset = self.audioTimeStamps[markersMappingIndexs[index]]    
            onsetIndex = markersMappingIndexs[index]
            try:
                duration = markersMappingIndexs[index+1] - onsetIndex
            except:
                duration = 0
            events.append([event, block, onset, duration, onsetIndex])
        self.audioEvents = events
        print('***************************Audio events mapped***************************')  
        

    
