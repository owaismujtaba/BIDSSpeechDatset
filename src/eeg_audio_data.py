import src.config as config
from src.utils import findClosestStartingIndex

import csv
import pdb
import os
from pathlib import Path
import mne
import json
from datetime import datetime
from scipy.io.wavfile import write
import numpy as np

class EegAudioDataProcessor:
        def __init__(self, eegData, audioData, subjectID, sessionID, runID, taskName):
                """
                Initialize the class with EEG and audio data.

                Parameters:
                eegData (object): An object containing EEG event data.
                audioData (object): An object containing audio event data.
                """
                self.eegData = eegData
                self.audioData = audioData
                self.audioSampleRate = 44100
                self.eegSampleRate = int(self.eegData.samplingFrequency)


                self.subjectID = subjectID
                self.sessionID = sessionID
                self.taskName = taskName
                self.runID = runID
                self.fileName = f'{self.subjectID}_ses-{self.sessionID}_task-{self.taskName}_run-{self.runID}'
                self.destinationDir = Path(config.bidsDir, self.subjectID)
                self.synchronizeEegAudioEvents()
                self.createEventsFile()
                self.createFifFile()
                self.createJsonFile()
                self.createAudio()

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
                print(f'Processing for {self.fileName}')
                eegEvents = self.eegData.eegEvents
                audioEvents = self.audioData.audioEvents

                eegEventsTimestamps = np.array([row[2] for row in eegEvents])
                audioEventsStartTime = audioEvents[0][2]        
                
                closestStartingPointInEeg = findClosestStartingIndex(eegEventsTimestamps, audioEventsStartTime)
                eegEvents = eegEvents[closestStartingPointInEeg:]
                
                audioEventTrackingIndex = 0
                synchronizedEvents = []
                for audioIndex in range(len(audioEvents)):
                        audioEvent = audioEvents[audioIndex][0].split(":")
                        try:
                                word = audioEvent[1]
                        except:
                                word = None
                        
                        audioEvent = audioEvent[0] 
                        block = audioEvents[audioIndex][1]
                        audioOnsetIndex = audioEvents[audioIndex][4]
                        audioOnsetTime = audioOnsetIndex/self.audioSampleRate
                        audioDuration = audioEvents[audioIndex][3]/self.audioSampleRate

                        if 'StartReading' in audioEvent or 'StartSaying'in audioEvent:
                                for eegIndex in range(audioEventTrackingIndex, len(eegEvents)):
                                        eegEvent = eegEvents[eegIndex][0]
                                        eegOnsetIndex = eegEvents[eegIndex][4]
                                        eegOnsetTime = eegOnsetIndex/self.eegSampleRate
                                        eegDuration = eegEvents[eegIndex][3]
                                        
                                        if eegEvent == audioEvent:
                                                audioEventTrackingIndex = eegIndex + 1
                                                synchronizedEvents.append(
                                                        [eegOnsetTime, eegDuration, eegOnsetIndex, 
                                                        audioOnsetTime, audioDuration, audioOnsetIndex,
                                                        eegEvents[eegIndex][2], audioEvents[audioIndex][2],
                                                        block, eegEvent, word]
                                                )
                                                
                                                break
                
                self.synchronizedEvents = synchronizedEvents
                self.nTrials = len(self.synchronizedEvents)

                print('***************************EEG and Audio Events synchronized***************************') 

        def createEventsFile(self):
                """
                Write synchronized events to a file, that contains onset, duration, trial type, block and audio
                info as well 
                Returns:
                None
                """
                print('***************************Writing events to file***************************')
                fileName = self.fileName + '.tsv'
                bidsHeaders = config.bidsEventsHeader
                destinationDir = Path(self.destinationDir, 'eeg')
                os.makedirs(destinationDir, exist_ok=True)
                fileNameWithPath = Path(destinationDir, fileName)       
                
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
        
        def createAudio(self):
                print('***************************Creating Audio file***************************')
                destinationDir = Path(self.destinationDir, 'audio')
                os.makedirs(destinationDir, exist_ok=True)
                audioData = self.audioData.audio
                destinationPath = Path(destinationDir, self.fileName+'.wav')
                write(destinationPath, self.audioSampleRate, audioData)
                print('***************************Audio file created***************************')

        def createFifFile(self):
                print('***************************Creating BIDS FIF file***************************')
                rawData = self.eegData.rawData.get_data()
                self.info  = self.eegData.rawData.info
                destinationDir = Path(self.destinationDir, 'eeg')
                os.makedirs(destinationDir, exist_ok=True)
                filepath = Path(destinationDir, self.fileName + '.fif')
                self.newData = mne.io.RawArray(rawData, self.info)
                self.newData.save(filepath, overwrite=True)
                print('***************************BIDS FIF file created***************************')
        
        def createJsonFile(self):
                print('***************************Creating JSON file***************************')
                destinationDir = Path(self.destinationDir, 'eeg')
                os.makedirs(destinationDir, exist_ok=True)
                filepath = Path(destinationDir, self.fileName + '.json')
                metaData = {
                        'creation_date': self.info['meas_date'].strftime('%Y-%m-%dT%H:%M:%S'),
                        'clean_date': str(datetime.now()),
                        'subject_id': self.subjectID,
                        'session_id': self.sessionID,
                        'run_id': self.runID,
                        'task_name': self.taskName,
                        'num_of_trials':self.nTrials,
                        'eeg_sampling_rate': self.eegSampleRate,
                        'audio_sampling_rate': self.audioSampleRate,
                        'number_of_channels': len(self.info['ch_names']),
                        'highpass': self.info['highpass'],
                        'lowpass': self.info['lowpass'],
                        'bads': self.info['bads'],
                        'Institute': 'CITIC-UGR, University of Granada',
                        'Address': 'Calle Periodista Rafael Gómez Montero 2, 18014, Granada',
                        'Authors': 'Jose Andres, Owais Mujtaba, Marc Ouellet',
                        'eeg_channels': self.info['ch_names'],
                }

                with open(filepath, 'w') as jsonFile:
                        json.dump(metaData, jsonFile, indent=4)

                print('***************************JSON file created***************************')
