from src.eeg_data_utils import EegDataProcessor
from src.audio_data_utils import AudioDataProcessor
from src.eeg_audio_data import EegAudioDataProcessor

import pdb

filepathEeg = '/home/owaismujtaba/BIDSSpeechDatset/rawData/F10/VCV/GOMEZCARMONA~ _67e7880a-4065-4e37-a165-58982f5f8c3c.edf'
filepathAudio = '/home/owaismujtaba/BIDSSpeechDatset/rawData/F10/VCV/sub-MartaGomezCarmona_ses-VCV_Ses01_task-Default_run-001_eeg.xdf'

eegData = EegDataProcessor(filepathEeg)
audioData = AudioDataProcessor(filepathAudio)

eegAudioData = EegAudioDataProcessor(eegData, audioData) 

pdb.set_trace()