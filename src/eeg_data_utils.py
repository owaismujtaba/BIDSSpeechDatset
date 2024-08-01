import src.config as config
from src.utils import loadEdfFile, eegNormalizeTriggers
from src.utils import eegCorrectTriggers, eegTransitionTriggerPoints
from src.utils import triggerEncodings
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
        print('***************************EEG Data Processing***************************')
        self.triggersNormalized = eegNormalizeTriggers(self.triggers)
        self.correctedTriggers = eegCorrectTriggers(self.triggersNormalized)
        self.eegTriggerTransitionPoints = eegTransitionTriggerPoints(
            self.correctedTriggers
        )  
        self.eegEvents = self.mapEegEvents(
            self.correctedTriggers, 
            self.eegTriggerTransitionPoints, 
            self.timeStamps
        )
        print('***************************EEG Data Processing Completed***************************')

    def mapEegEvents(self, triggerArray, triggerTransitionPoints, timestamps):
        """
        Maps EEG trigger values to their corresponding start and end points.

        This function takes an array of trigger values, an array of trigger points (indexes where trigger 
        values change), and an array of timestamps. It identifies events based on the trigger values and 
        maps them to their start and end points. Each event is represented by its corresponding marker 
        name, start timestamp, end timestamp, start index, end index, and duration.

        Parameters:
        triggerArray (np.ndarray): An array of trigger values recorded during the EEG session.
        triggerTransitionPoints (np.ndarray): An array of indexes in the trigger values array where the trigger values change.
        timestamps (np.ndarray): An array of timestamps corresponding to the trigger values.

        Returns:
        List[List]: A list of lists, each representing an event with the following information:
                - Marker name (str)
                - Start timestamp (float)
                - End timestamp (float)
                - Start index (int)
                - End index (int)
                - Duration (int)
            
        Example:
        >>> triggerArray = np.array([0, 0, 1, 1, 0, 0, 2, 2, 0])
        >>> triggerPoints = np.array([0, 2, 6])
        >>> timestamps = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
        >>> EegEventsMapping(triggerArray, triggerPoints, timestamps)
            [['StartReading', 0.0, 1.0, 0, 2, 2],
            ['EndReading', 2.0, 3.0, 6, 8, 2]]
        """
        print('***************************Mapping EEG events***************************')  
        events = []
        block = None
        for i in range(triggerTransitionPoints.shape[0] - 1):
                
            onsetIndex = triggerTransitionPoints[i]
            endIndex = triggerTransitionPoints[i + 1]
            event = triggerEncodings(triggerArray[onsetIndex])
            onset = timestamps[onsetIndex]
            if 'BlockSaying' in event:
                block = 'Overt'
            if 'BlockThinking' in event:
                block = 'Inert'
            duration = endIndex - onsetIndex
            if duration < 25:
                continue
            events.append([event, block, onset , duration, onsetIndex])
        print('***************************EEG events mapped***************************')
        return events
                
