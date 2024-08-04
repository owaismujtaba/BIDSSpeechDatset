from src.eeg_data_utils import EegDataProcessor
from src.audio_data_utils import AudioDataProcessor
from src.eeg_audio_data import EegAudioDataProcessor

import pdb

filepathEeg = '/home/owaismujtaba/projects/BIDSSpeechDatset/rawData/F01/VCV/RAELARRIBAS~ V_7f515438-77ab-4fcd-9b71-60915d793845.edf'
filepathAudio = '/home/owaismujtaba/projects/BIDSSpeechDatset/rawData/F01/VCV/sub-VanesaRaelArribas_ses-Ses01_task-Default_run-001_eeg.xdf'
subjectID = 'F01'
sessionID = '01'
runID = '01'
taskName = 'VCV'

eegData = EegDataProcessor(filepathEeg)
audioData = AudioDataProcessor(filepathAudio)

eegAudioData = EegAudioDataProcessor(eegData=eegData, 
                                audioData=audioData,
                                taskName=taskName,
                                subjectID=subjectID,
                                sessionID=sessionID,
                                runID=runID 
    ) 

pdb.set_trace()