import os
import csv
import json
from pathlib import Path
from datetime import datetime

import mne
import numpy as np
import pyedflib
from scipy.io.wavfile import write

import src.config as config
from src.utils import findClosestStartingIndex


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
        self.destinationDir = Path(f'{config.bidsDir}/{self.subjectID}')
        self.fileName = f'{self.subjectID}_ses-{self.sessionID}_task-{self.taskName}_run-{self.runID}'
        self.ensureDirectoryExists(self.destinationDir)

        self.synchronizeEegAudioEvents()
        self.createAnnotations()
        self.createEventsFile()
        self.createEdfFile()
        self.createJsonFile()

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
        self.onset, self.duration, self.description = zip(*[
            (event[0], event[1], f'{event[-2]}_{event[-1]}') for event in self.synchronizedEvents
        ])

    def createEdfFile(self):
        """Create an EDF file with EEG and audio data.

        Returns:
        Path: The path of the created EDF file.
        """
        signals = list(self.eegData.rawData.get_data())
        audioData = self.audioData.audio.flatten()
        channelNames = list(self.eegData.channelNames)

        data, channelNames, samplingFrequencies = self.checkValidityOfSignals(
            signals=signals,
            sampleFrequency=self.eegSampleRate,
            channelNames=channelNames
        )
        
        data.append(audioData)
        channelNames.append('Audio')
        samplingFrequencies.append(self.audioSampleRate)

        destinationDir = self.destinationDir / 'eeg'
        self.ensureDirectoryExists(destinationDir)
        filePath = destinationDir / f'{self.fileName}_eeg.edf'

        with pyedflib.EdfWriter(str(filePath), len(channelNames), file_type=pyedflib.FILETYPE_EDFPLUS) as f:
            for i, channelName in enumerate(channelNames):
                f.setSignalHeader(i, {
                    'label': channelName,
                    'dimension': 'uV',
                    'sample_rate': samplingFrequencies[i],
                    'physical_max': data[i].max(),
                    'physical_min': data[i].min(),
                    'digital_max': 32767,
                    'digital_min': -32768,
                    'prefilter': '',
                    'n_samples': data[i].shape[0]
                })

            f.writeSamples(data)

            for onset, duration, description in zip(self.onset, self.duration, self.description):
                f.writeAnnotation(
                    onset_in_seconds=onset,
                    duration_in_seconds=duration,
                    description=description
                )

        return filePath

    def checkValidityOfSignals(self, signals, sampleFrequency, channelNames):
        """Check the validity of signals and return only valid ones.

        Parameters:
        signals (list): The list of signal arrays.
        sampleFrequency (int): The sample frequency of the signals.
        channelNames (list): The names of the channels.

        Returns:
        tuple: Contains valid data, channel names, and sampling frequencies.
        """
        data, chNames, sampFreq = [], [], []
        for index in range(len(signals)):
            if signals[index].min() != signals[index].max():
                data.append(signals[index])
                chNames.append(channelNames[index])
                sampFreq.append(sampleFrequency)

        return data, chNames, sampFreq

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

    def createEventsFile(self):
        """Write synchronized events to a TSV file.

        Returns:
        Path: The path of the created events file.
        """
        print('***************************Writing events to file***************************')
        fileName = f'{self.fileName}_events.tsv'
        bidsHeaders = config.bidsEventsHeader
        destinationDir = self.destinationDir / 'eeg'
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
        destinationPath = destinationDir / f'{self.fileName}_.wav'
        write(str(destinationPath), self.audioSampleRate, audioData)
        print('***************************Audio file created***************************')

        return destinationPath

    def createFifFile(self):
        """Create a BIDS FIF file from the EEG data.

        Returns:
        Path: The path of the created FIF file.
        """
        print('***************************Creating BIDS FIF file***************************')
        rawData = self.eegData.rawData.get_data()
        self.info = self.eegData.rawData.info
        destinationDir = self.destinationDir / 'eeg'
        self.ensureDirectoryExists(destinationDir)
        filePath = destinationDir / f'{self.fileName}_eeg.fif'
        self.newData = mne.io.RawArray(rawData, self.info)
        self.newData.set_annotations(self.annotations)
        self.newData.save(str(filePath), overwrite=True)
        print('***************************BIDS FIF file created***************************')

        return filePath
        
    def createJsonFile(self):
        """Create a JSON metadata file.

        Returns:
        Path: The path of the created JSON file.
        """
        print('***************************Creating JSON file***************************')
        destinationDir = self.destinationDir / 'eeg'
        self.ensureDirectoryExists(destinationDir)
        filePath = destinationDir / f'{self.fileName}_eeg.json'
        
        metaData = {
            'creation_date': self.info['meas_date'].strftime('%Y-%m-%dT%H:%M:%S'),
            'clean_date': str(datetime.now()),
            'subject_id': self.subjectID,
            'session_id': self.sessionID,
            'run_id': self.runID,
            'task_name': self.taskName,
            'num_trials': self.nTrials,
            'eeg_sampling_rate': self.eegSampleRate,
            'audio_sampling_rate': self.audioSampleRate,
            'number_of_channels': len(self.info['ch_names']),
            'highpass': self.info['highpass'],
            'lowpass': self.info['lowpass'],
            'bads': self.info['bads']
        }

        with open(filePath, 'w') as jsonFile:
            json.dump(metaData, jsonFile, indent=4)

        print('***************************JSON file created***************************')
        return filePath
