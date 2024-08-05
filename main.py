from src.eeg_data_utils import EegDataProcessor
from src.audio_data_utils import AudioDataProcessor
from src.eeg_audio_data import EegAudioDataProcessor

import pdb

filepathEeg = '/home/owais/BIDSSpeechDatset/rawData/F09/VCV/JIMÉNEZÁLVAREZ_605b2177-7b18-4d5b-a6df-01fdc6572770.edf'
filepathAudio = '/home/owais/BIDSSpeechDatset/rawData/F09/VCV/sub-AntoniaJimenezAlvarez_ses-VCV_Ses01_task-Default_run-001_eeg.xdf'
subjectID = 'F09'
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

