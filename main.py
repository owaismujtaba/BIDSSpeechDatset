from src.eeg_data_utils import EegDataProcessor
from src.audio_data_utils import AudioDataProcessor
from src.eeg_audio_data import EegAudioDataProcessor

import pdb

filepathEeg = '/home/owaismujtaba/projects/BIDSSpeechDatset/rawData/F05/VCV/Day01/JURCICIENE~ ED_30db7f57-f064-4c1c-a2ac-86eeea186668.edf'
filepathAudio = '/home/owaismujtaba/projects/BIDSSpeechDatset/rawData/F05/VCV/Day01/sub-Edita_ses-S002_task-Default_run-001_eeg.xdf'
subjectID = 'F05'
sessionID = '01'
runID = '02'
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

