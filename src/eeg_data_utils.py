import src.config as config
from src.utils import loadEdfFile
import pdb

class EegData:
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
        self.timeStamps = self.rawData.times + self.rawData.info['meas_date'].timestamp()
        self.goodChannels = [item for item in self.channelNames if item not in self.badChannels]
