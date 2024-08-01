import src.config as config
<<<<<<< HEAD
=======
from src.utils import findClosestStartingPointInEeg
>>>>>>> 9aed453 (synchronizing)
import csv
import pdb
import os
from pathlib import Path
import mne
<<<<<<< HEAD
=======
import json
import numpy as np
>>>>>>> 9aed453 (synchronizing)

class EegAudioDataProcessor:
    def __init__(self, eegData, audioData):
        """
        Initialize the class with EEG and audio data.

        Parameters:
        eegData (object): An object containing EEG event data.
        audioData (object): An object containing audio event data.
        """
        self.eegData = eegData
        self.audioData = audioData
<<<<<<< HEAD
        self.subjectID = 'F10'
        self.sessionID = '01'
=======
        self.subjectID = 'F01'
        self.sessionID = '02'
>>>>>>> 9aed453 (synchronizing)
        self.taskName = 'VCV'
        self.runID = '01'
        self.fileName = f'sub-{self.subjectID}_ses-{self.sessionID}_task-{self.taskName}_run-{self.runID}'
        self.synchronizeEegAudioEvents()
<<<<<<< HEAD
        self.eventsFileWriter()
        self.createBidsFifFile()
        pdb.set_trace()
=======
        #self.createBidsFifFile()
        
>>>>>>> 9aed453 (synchronizing)

    def synchronizeEegAudioEvents(self):
        """
        Synchronize EEG and audio events based on their onset times and event types.

        The function matches EEG events with corresponding audio events where the event
        types are the same ('StartReading' or 'StartSaying'). It then records synchronized
        details including onset times, durations, and the word associated with the audio event.

        Returns:
        None: The synchronized events are stored in the instance attribute `self.synchronizedEvents`.
        """
        
        print('***************************Synchronizing EEG and Audio Events***************************')
        eegEvents = self.eegData.eegEvents
        audioEvents = self.audioData.audioEvents
<<<<<<< HEAD

=======
        eegClosestStartingPointIndex = findClosestStartingPointInEeg(eegEvents, audioEvents[0][2])
        eegEvents = eegEvents[eegClosestStartingPointIndex:]    
        
>>>>>>> 9aed453 (synchronizing)
        audioEventTrackingIndex = 0
        synchronizedEvents = []
        words = []
        for audioindex in range(len(audioEvents)):
            audioEvent = audioEvents[audioindex][0].split(":")
            try:
                word = audioEvent[1]
            except:
                word = None
            audioEvent = audioEvent[0] 
            block = audioEvents[audioindex][1]
            audioOnset = audioEvents[audioindex][2]
            audioOnsetIndex = audioEvents[audioindex][4]
            audioDuration = audioEvents[audioindex][3]
            if 'StartReading' in audioEvent or 'StartSaying'in audioEvent:
                for eegIndex in range(audioEventTrackingIndex, len(eegEvents)):
                    eegEvent = eegEvents[eegIndex][0]
<<<<<<< HEAD
                    eegOnset = eegEvents[eegIndex][2]/self.eegData.samplingFrequency
=======
                    eegOnset = eegEvents[eegIndex][2]
>>>>>>> 9aed453 (synchronizing)
                    eegOnsetIndex = eegEvents[eegIndex][4]
                    eegDuration = eegEvents[eegIndex][3]
                    if eegEvent == audioEvent:
                        words.append(word)
                        audioEventTrackingIndex = eegIndex + 1
                        synchronizedEvents.append([eegEvent, block, audioOnsetIndex/self.audioData.samplingFrequency, 
                                                   audioDuration/self.audioData.samplingFrequency, audioOnsetIndex, 
                                                   eegOnsetIndex/self.eegData.samplingFrequency, 
<<<<<<< HEAD
                                                   eegDuration/self.eegData.samplingFrequency, eegOnsetIndex, word 
=======
                                                   eegDuration/self.eegData.samplingFrequency, eegOnsetIndex, word,
                                                   eegOnset, audioOnset 
>>>>>>> 9aed453 (synchronizing)
                        ])
                        
                        break
            else:
                continue
        
        self.synchronizedEvents = synchronizedEvents

        print('***************************EEG and Audio Events synchronized***************************') 

<<<<<<< HEAD

    def eventsFileWriter(self):
=======
    def eventsFileWriter(self, destinationDir):
>>>>>>> 9aed453 (synchronizing)
        """
        Write synchronized events to a file.
        Returns:
        None
        """
        print('***************************Writing events to file***************************')
        fileName = self.fileName + '_events.tsv'
<<<<<<< HEAD
        bidsHeaders = config.bidsEventsHeader
        
        with open(fileName, "w", newline="") as tsvfile:
=======
        filepath = Path(destinationDir, fileName)
        bidsHeaders = config.bidsEventsHeader
        
        with open(filepath, "w", newline="") as tsvfile:
>>>>>>> 9aed453 (synchronizing)
            writer = csv.DictWriter(tsvfile, fieldnames=bidsHeaders, delimiter='\t')
            writer.writeheader()

            for row in self.synchronizedEvents:
                event = {
                    "onset": row[5],  
                    "duration": row[6], 
                    "trial_type": row[0],
                    "block": row[1],
                    "audioOnset": row[2],  
                    "audioDuration": row[3],  
                    "audioOnsetIndex": row[4],
                    "eegOnsetIndex": row[7],
                    "word": row[8]
                }
                writer.writerow(event)
        
        print('***************************Events written to file***************************')

<<<<<<< HEAD




=======
>>>>>>> 9aed453 (synchronizing)
    def createBidsFifFile(self):
        print('***************************Creating BIDS FIF file***************************')
        rawData = self.eegData.rawData.get_data()
        info  = self.eegData.rawData.info
<<<<<<< HEAD
        pdb.set_trace()
=======
        
>>>>>>> 9aed453 (synchronizing)
        rootDir = config.bidsDir
        os.makedirs(rootDir, exist_ok=True)
        destinationDir = f'{rootDir}/{self.subjectID}/eeg'
        destinationPath = Path(destinationDir)
        os.makedirs(destinationPath, exist_ok=True)

        filepath = Path(destinationDir, self.fileName + '_eeg.fif')

<<<<<<< HEAD
        newData = mne.io.RawArray(rawData, info)
        newData.save(filepath, overwrite=True)
=======
        self.newFifData = mne.io.RawArray(rawData, info)
        self.newFifData.save(filepath, overwrite=True)
        print('***************************BIDS FIF file created***************************')    
        self.eventsFileWriter(destinationDir)
        self.createJsonFile(destinationDir)

    def createJsonFile(self, destinationDir):
        info = self.eegData.rawData.info
        
        metadata = {
            'TaskName': self.taskName,  
            'SubjectID': self.subjectID,
            'SessionID': self.sessionID,
            'RunID': self.runID,
            'NoOfTrials':len(self.synchronizedEvents),
            'SamplingFrequency': info['sfreq'],
            'Manufacturer': 'Unknown',  
            'EEGReference': 'Unknown',  
            'EEGChannelCount': info['nchan'],
            'EEGPlacementScheme': '10-20', 
            'RecordingDuration': self.newFifData.times[-1],  
            'RecordingType': 'continuous',
            'EpochLength': 'n/a',
            'HardwareFilters': {
                'Highpass': info['highpass'],
                'Lowpass': info['lowpass']
            },
            'DateOfRecording': info['meas_date'].strftime('%Y-%m-%dT%H:%M:%S') if info['meas_date'] is not None else 'n/a',
            'InstitutionName': 'CITIC-UGR, University of Granada', 
            'InstitutionAddress': 'Calle Periodista Rafael Gomez Montero 2, 18014, Granada ',  
        }
        filepath = Path(destinationDir, self.fileName + '_eeg.json')
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=4)

        
    def setAnnotations(self):
        for event in self.synchronizedEvents:
            print(event)
>>>>>>> 9aed453 (synchronizing)
