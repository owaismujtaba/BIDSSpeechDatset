import os
import csv
import pdb
from pathlib import Path


import mne
import numpy as np
from scipy.io.wavfile import write

import src.config as config
from src.utils import findClosestStartingIndex
from mne_bids import BIDSPath, write_raw_bids

class EegAudioDataProcessor:

    def __init__(self, eegData, audioData, subjectID, sessionID, runID, taskName):
        """
        Initialize the class with EEG and audio data.

        Parameters:
        eegData (object): An object containing EEG event data.
        audioData (object): An object containing audio event data.
        subjectID (str): The ID of the subject.
        sessionID (str): The session ID.
        runID (str): The run ID.
        taskName (str): The name of the task.
        """
        self.eegData = eegData
        self.audioData = audioData
        self.audioSampleRate = 44100
        self.eegSampleRate = int(self.eegData.samplingFrequency)
        self.info = self.eegData.rawData.info

        self.subjectID = subjectID
        self.sessionID = sessionID
        self.taskName = taskName
        self.runID = runID
        self.destinationDir = Path(f'{config.bidsDir}/sub-{self.subjectID}/ses-{sessionID}')
        self.fileName = f'sub-{self.subjectID}_ses-{self.sessionID}_task-{self.taskName}_run-{self.runID}'

        self.bidsPath = BIDSPath(
            subject=self.subjectID, session=self.sessionID,
            task='VCV', run='01', datatype='eeg', root=config.bidsDir
        )

        self.synchronizeEegAudioEvents()
        self.createAnnotations()
        self.createEDFFile()
        self.createAudio()
        self.createEventsFileForAudio()
        #self.createJsonFile()
        

    def ensureDirectoryExists(self, path):
        """Ensure that the given directory exists.

        Parameters:
        path (Path): The path to check/create.
        """
        os.makedirs(path, exist_ok=True)

    def createAnnotations(self):
        """Create annotations from synchronized events.

        Returns:
        tuple: Contains lists of onsets, durations, and descriptions.
        """
        onset, duration, description = zip(*[
            (event[0], event[1], f'{event[-3]}_{event[-2]}_{event[-1]}') for event in self.synchronizedEvents
        ])

        self.annotations = mne.Annotations(
            onset=onset,
            duration=duration,
            description=description
        )

    def synchronizeEegAudioEvents(self):
        """Synchronize EEG and audio events based on their onset times and event types.

        Returns:
        list: A list of synchronized events.
        """
        print('***************************Synchronizing EEG and Audio Events***************************')
        print(f'Processing for {self.fileName}')
        eegEvents = self.eegData.eegEvents
        audioEvents = self.audioData.audioEvents

        eegEventsTimestamps = np.array([row[2] for row in eegEvents])
        audioEventsStartTime = audioEvents[0][2]        

        closestStartingPointInEeg = findClosestStartingIndex(eegEventsTimestamps, audioEventsStartTime)
        eegEvents = eegEvents[closestStartingPointInEeg:]

        synchronizedEvents = []
        audioEventTrackingIndex = 0
        
        for audioIndex, audioEvent in enumerate(audioEvents):
            audioEventName = audioEvent[0].split(":")[0] 
            try:
                word = audioEvent[0].split(":")[1] 
            except:
                word = None
            audioOnsetIndex = audioEvent[4]
            audioOnsetTime = audioOnsetIndex / self.audioSampleRate
            audioDuration = audioEvent[3] / self.audioSampleRate

            if True:
                for eegIndex in range(audioEventTrackingIndex, len(eegEvents)):
                    eegEventName = eegEvents[eegIndex][0]
                    eegOnsetIndex = eegEvents[eegIndex][4]
                    eegOnsetTime = eegOnsetIndex / self.eegSampleRate
                    eegDuration = eegEvents[eegIndex][3] / self.eegSampleRate

                    if eegEventName == audioEventName:
                        audioEventTrackingIndex = eegIndex + 1
                        synchronizedEvents.append([
                            eegOnsetTime, eegDuration, eegOnsetIndex,
                            audioOnsetTime, audioDuration, audioOnsetIndex,
                            eegEvents[eegIndex][2], audioEvents[audioIndex][2],
                            audioEvent[1], eegEventName, word
                        ])
                        break
        
        self.synchronizedEvents = synchronizedEvents
        self.nTrials = len(self.synchronizedEvents)

        print('***************************EEG and Audio Events synchronized***************************') 
        return synchronizedEvents


    def synchronizeEegAudioEvents1(self):
        """Synchronize EEG and audio events based on their onset times and event types.

        Returns:
        list: A list of synchronized events.
        """
        print('***************************Synchronizing EEG and Audio Events***************************')
        print(f'Processing for {self.fileName}')
        eegEvents = self.eegData.eegEvents
        audioEvents = self.audioData.audioEvents

        eegEventsTimestamps = np.array([row[2] for row in eegEvents])
        audioEventsStartTime = audioEvents[0][2]        

        closestStartingPointInEeg = findClosestStartingIndex(eegEventsTimestamps, audioEventsStartTime)
        eegEvents = eegEvents[closestStartingPointInEeg:]

        synchronizedEvents = []
        audioEventTrackingIndex = 0
        
        for audioIndex, audioEvent in enumerate(audioEvents):
            audioEventName = audioEvent[0].split(":")[0] 
            try:
                word = audioEvent[0].split(":")[1] 
            except:
                word = None
            audioOnsetIndex = audioEvent[4]
            audioOnsetTime = audioOnsetIndex / self.audioSampleRate
            audioDuration = audioEvent[3] / self.audioSampleRate

            if 'StartReading' in audioEventName or 'StartSaying' in audioEventName:
                for eegIndex in range(audioEventTrackingIndex, len(eegEvents)):
                    eegEventName = eegEvents[eegIndex][0]
                    eegOnsetIndex = eegEvents[eegIndex][4]
                    eegOnsetTime = eegOnsetIndex / self.eegSampleRate
                    eegDuration = eegEvents[eegIndex][3] / self.eegSampleRate

                    if eegEventName == audioEventName:
                        audioEventTrackingIndex = eegIndex + 1
                        synchronizedEvents.append([
                            eegOnsetTime, eegDuration, eegOnsetIndex,
                            audioOnsetTime, audioDuration, audioOnsetIndex,
                            eegEvents[eegIndex][2], audioEvents[audioIndex][2],
                            audioEvent[1], eegEventName, word
                        ])
                        break
        
        self.synchronizedEvents = synchronizedEvents
        self.nTrials = len(self.synchronizedEvents)

        print('***************************EEG and Audio Events synchronized***************************') 
        return synchronizedEvents

    def createEventsFileForAudio(self):
        """Write synchronized events to a TSV file.

        Returns:
        Path: The path of the created events file.
        """
        print('***************************Writing events to file***************************')
        fileName = f'{self.fileName}_events.tsv'
        bidsHeaders = config.bidsEventsHeader
        destinationDir = self.destinationDir / 'audio'
        self.ensureDirectoryExists(destinationDir)
        fileNameWithPath = destinationDir / fileName       

        with open(fileNameWithPath, "w", newline="") as tsvfile:
            writer = csv.DictWriter(tsvfile, fieldnames=bidsHeaders, delimiter='\t')
            writer.writeheader()

            for row in self.synchronizedEvents:
                event = {
                    "onset": row[0],  
                    "duration": row[1],
                    "eegOnsetIndex": row[2], 
                    "audioOnset": row[3],  
                    "audioDuration": row[4],  
                    "audioOnsetIndex": row[5],
                    "eegOnsetUnixTime": row[6],
                    "audioOnsetUnixTime": row[7],
                    "block": row[8],
                    "trialType": row[9],
                    "word": row[10]
                }
                writer.writerow(event)

        print('***************************Events written to file***************************')
        return fileNameWithPath
        
    def createAudio(self):
        """Create an audio file from audio data.

        Returns:
        Path: The path of the created audio file.
        """
        print('***************************Creating Audio file***************************')
        destinationDir = self.destinationDir / 'audio'
        self.ensureDirectoryExists(destinationDir)
        audioData = self.audioData.audio
        destinationPath = destinationDir / f'{self.fileName}_audio.wav'
        write(str(destinationPath), self.audioSampleRate, audioData)
        print('***************************Audio file created***************************')

        return destinationPath

    def createEDFFile(self):
        """Create a BIDS FIF file from the EEG data.

        Returns:
        Path: The path of the created FIF file.
        """
        print('***************************Creating BIDS FIF file***************************')
        rawData = self.eegData.rawData.get_data()
        self.info = self.eegData.rawData.info

        self.newData = mne.io.RawArray(rawData, self.info)
        self.newData.set_annotations(self.annotations)
        
        
        write_raw_bids(self.newData, bids_path=self.bidsPath, allow_preload=True, format='EDF', overwrite=True)
       
        
        print('***************************BIDS FIF file created***************************')

    
        
    
