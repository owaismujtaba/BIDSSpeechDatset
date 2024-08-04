import src.config as config
from src.utils import findClosestStartingIndex

import csv
import pdb
import os
from pathlib import Path
import mne
import json
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
                self.audioSampleRate = int(self.audioData.samplingFrequency)
                self.eegSampleRate = int(self.eegData.samplingFrequency)


                self.subjectID = subjectID
                self.sessionID = sessionID
                self.taskName = taskName
                self.runID = runID
                self.fileName = f'sub-{self.subjectID}_ses-{self.sessionID}_task-{self.taskName}_run-{self.runID}'
                self.destinationDir = Path(f'{config.bidsDir}/{self.subjectID}/eeg')
                self.synchronizeEegAudioEvents()
                self.eventsFileWriter()
                self.createBidsFifFile()

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

                eegEventsTimestamps = np.array([row[2] for row in eegEvents])
                audioEventsStartTime = audioEvents[0][2]        
                
                closestStartingPointInEeg = findClosestStartingIndex(eegEventsTimestamps, audioEventsStartTime)
                eegEvents = eegEvents[closestStartingPointInEeg:]
                
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
                audioOnsetIndex = audioEvents[audioindex][4]
                audioOnsetTime = audioOnsetIndex/self.audioSampleRate
                audioDuration = audioEvents[audioindex][3]/self.audioSampleRate

                if 'StartReading' in audioEvent or 'StartSaying'in audioEvent:
                        for eegIndex in range(audioEventTrackingIndex, len(eegEvents)):
                        eegEvent = eegEvents[eegIndex][0]
                        eegOnsetIndex = eegEvents[eegIndex][4]
                        eegOnsetTime = eegOnsetIndex/self.eegSampleRate
                        eegDuration = eegEvents[eegIndex][3]
                        
                        if eegEvent == audioEvent:
                                words.append(word)
                                audioEventTrackingIndex = eegIndex + 1
                                synchronizedEvents.append(
                                [
                                        eegOnsetTime, eegDuration, eegOnsetIndex, 
                                        audioOnsetTime, audioDuration, audioOnsetIndex,
                                        block, eegEvent, word
                                ]
                                )
                                
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
                fileNameWithPath = Path(self.destinationDir, fileName)
                os.makedirs(self.destinationDir, exist_ok=True)

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
                        "block": row[6],
                        "trialType": row[7],
                        "word": row[8]
                        }
                        writer.writerow(event)
                
                print('***************************Events written to file***************************')
        
        def createBidsFifFile(self):
                print('***************************Creating BIDS FIF file***************************')
                rawData = self.eegData.rawData.get_data()
                info  = self.eegData.rawData.info

                os.makedirs(self.destinationDir, exist_ok=True)
                filepath = Path(self.destinationDir, self.fileName + '_eeg.fif')
                newData = mne.io.RawArray(rawData, info)
                newData.save(filepath, overwrite=True)
        def createJsonFile():
                pass
