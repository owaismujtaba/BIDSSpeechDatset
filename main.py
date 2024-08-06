from src.eeg_data_utils import EegDataProcessor
from src.audio_data_utils import AudioDataProcessor
from src.eeg_audio_data import EegAudioDataProcessor

import pdb

filepathEeg   = r'C:\Projects\BIDSSpeechDatset\RawData\F10\VCV\Day01\GOMEZCARMONA~ _67e7880a-4065-4e37-a165-58982f5f8c3c.edf'
filepathAudio = r'C:\Projects\BIDSSpeechDatset\RawData\F10\VCV\Day01\sub-MartaGomezCarmona_ses-VCV_Ses01_task-Default_run-001_eeg.xdf'

subjectID = 'sub-10'
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

