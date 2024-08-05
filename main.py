from src.eeg_data_utils import EegDataProcessor
from src.audio_data_utils import AudioDataProcessor
from src.eeg_audio_data import EegAudioDataProcessor

import pdb

filepathEeg = '/home/owais/BIDSSpeechDatset/rawData/F07/VCV/Day02/GAMBOALÓPEZ~ S_a8df7304-f513-4268-bb9b-5cf7a3676dad.edf'
filepathAudio = '/home/owais/BIDSSpeechDatset/rawData/F07/VCV/Day02/sub-SoniaGamboaLopez_ses-VCV_Ses02_task-Default_run-001_eeg.xdf'
subjectID = 'F07'
sessionID = '02'
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

