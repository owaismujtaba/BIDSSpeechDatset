import src.config as config
import csv
import pdb
import os
from pathlib import Path
import mne

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
        self.subjectID = 'F10'
        self.sessionID = '01'
        self.taskName = 'VCV'
        self.runID = '01'
        self.fileName = f'sub-{self.subjectID}_ses-{self.sessionID}_task-{self.taskName}_run-{self.runID}'
        self.synchronizeEegAudioEvents()
        self.eventsFileWriter()
        self.createBidsFifFile()
        pdb.set_trace()

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
                    eegOnset = eegEvents[eegIndex][2]/self.eegData.samplingFrequency
                    eegOnsetIndex = eegEvents[eegIndex][4]
                    eegDuration = eegEvents[eegIndex][3]
                    if eegEvent == audioEvent:
                        words.append(word)
                        audioEventTrackingIndex = eegIndex + 1
                        synchronizedEvents.append([eegEvent, block, audioOnsetIndex/self.audioData.samplingFrequency, 
                                                   audioDuration/self.audioData.samplingFrequency, audioOnsetIndex, 
                                                   eegOnsetIndex/self.eegData.samplingFrequency, 
                                                   eegDuration/self.eegData.samplingFrequency, eegOnsetIndex, word 
                        ])
                        
                        break
            else:
                continue
        
        self.synchronizedEvents = synchronizedEvents

        print('***************************EEG and Audio Events synchronized***************************') 


    def eventsFileWriter(self):
        """
        Write synchronized events to a file.
        Returns:
        None
        """
        print('***************************Writing events to file***************************')
        fileName = self.fileName + '_events.tsv'
        bidsHeaders = config.bidsEventsHeader
        
        with open(fileName, "w", newline="") as tsvfile:
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





    def createBidsFifFile(self):
        print('***************************Creating BIDS FIF file***************************')
        rawData = self.eegData.rawData.get_data()
        info  = self.eegData.rawData.info
        pdb.set_trace()
        rootDir = config.bidsDir
        os.makedirs(rootDir, exist_ok=True)
        destinationDir = f'{rootDir}/{self.subjectID}/eeg'
        destinationPath = Path(destinationDir)
        os.makedirs(destinationPath, exist_ok=True)

        filepath = Path(destinationDir, self.fileName + '_eeg.fif')

        newData = mne.io.RawArray(rawData, info)
        newData.save(filepath, overwrite=True)