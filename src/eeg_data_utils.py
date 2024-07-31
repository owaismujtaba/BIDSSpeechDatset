import src.config as config
from src.utils import loadEdfFile, eegNormalizeTriggers
from src.utils import eegCorrectTriggers, eegTransitionTriggerPoints
from src.utils import eegEventsMapping
import pdb

class EegDataProcessor:
    def __init__(self, filepath):
        self.rawData = loadEdfFile(filepath)
        self.setupEegDataInfo()

    
    def setupEegDataInfo(self):
        
        self.nChannels = self.rawData.info['nchan']
        self.badChannels = list(self.rawData.info['bads'])
        self.startTime = self.rawData.info['meas_date']
        self.channelNames = self.rawData.ch_names
        self.samplingFrequency = self.rawData.info['sfreq']
        self.triggers = self.rawData['TRIG'][0][0]
        self.duration = self.rawData.n_times / self.samplingFrequency
        self.timeStamps = self.rawData.times + self.startTime.timestamp()
        self.goodChannels = [item for item in self.channelNames if item not in self.badChannels]
        self.processEegData()

    def processEegData(self):
        
        self.triggersNormalized = eegNormalizeTriggers(self.triggers)
        self.correctedTriggers = eegCorrectTriggers(self.triggersNormalized)
        self.eegTriggerTransitionPoints = eegTransitionTriggerPoints(
            self.correctedTriggers
        )  
        self.eegEvents = eegEventsMapping(
            self.correctedTriggers, 
            self.eegTriggerTransitionPoints, 
            self.timeStamps
        )

        
