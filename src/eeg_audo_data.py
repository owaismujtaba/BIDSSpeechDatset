

class EegAudioDataProcessor:
    def __init__(self, eegData, audioData):
        self.eegData = eegData
        self.audioData = audioData

    def synchronizeEegAudioData(self):
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
                    eegOnset = eegEvents[eegIndex][2]
                    eegOnsetIndex = eegEvents[eegIndex][4]
                    eegDuration = eegEvents[eegIndex][3]
                    if eegEvent == audioEvent:
                        words.append(word)
                        audioEventTrackingIndex = eegIndex + 1
                        synchronizedEvents.append([eegEvent, block, audioOnset, audioDuration, audioOnsetIndex, eegOnset, eegDuration, eegOnsetIndex, word ])
                        break
            else:
                continue
            
            