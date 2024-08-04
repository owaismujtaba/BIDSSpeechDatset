from src.eeg_data_utils import EegDataProcessor
from src.audio_data_utils import AudioDataProcessor
from src.eeg_audio_data import EegAudioDataProcessor

import pdb

filepathEeg = '/home/owaismujtaba/projects/BIDSSpeechDatset/rawData/F01/VCV/RAELARRIBAS~ V_7f515438-77ab-4fcd-9b71-60915d793845.edf'
filepathAudio = '/home/owaismujtaba/projects/BIDSSpeechDatset/rawData/F01/VCV/sub-VanesaRaelArribas_ses-Ses02_task-Default_run-001_eeg.xdf'

eegData = EegDataProcessor(filepathEeg)
audioData = AudioDataProcessor(filepathAudio)

eegAudioData = EegAudioDataProcessor(eegData, audioData) 

pdb.set_trace()