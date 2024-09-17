from src.eeg_data_utils import EegDataProcessor
from src.audio_data_utils import AudioDataProcessor
from src.eeg_audio_data import EegAudioDataProcessor
import src.config as config
from src.audio_analyser import AudioAnalyser

from src.gui.main_interface import MainWindow
from src.gui.mapping_page import EegAudioMappingWindow
import sys
from PyQt5.QtWidgets import QApplication
import pdb



if config.use_gui:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
else:
    subjectIDs = [
        '01', '01', '05', '05', '05', '07', '07', '08','09', '09',
        '10', '06', '06', '06', '11', '12'
    ]
    
    sessionIDs = [
        '01', '02', '01', '02', '03', '01', '02', '01', '01', '02',
        '01', '01', '02', '03', '01', '01'

    ]
    
    edfPaths = [
        'rawData/F01/VCV/RAELARRIBAS~ V_7f515438-77ab-4fcd-9b71-60915d793845.edf',
        'rawData/F01/VCV/RAELARRIBAS~ V_7f515438-77ab-4fcd-9b71-60915d793845.edf',
        'rawData/F05/VCV/Day01/JURCICIENE~ ED_30db7f57-f064-4c1c-a2ac-86eeea186668.edf',
        'rawData/F05/VCV/Day01/JURCICIENE~ ED_30db7f57-f064-4c1c-a2ac-86eeea186668.edf',
        'rawData/F05/VCV/Day02/JURCICIENE~ ED_89ffdaeb-4944-45a1-a956-62e24a0c1610.edf',
        'rawData/F07/VCV/Day01/universidad~ u_8cb40da1-81be-4ec9-a7d9-1949f755c395.edf',
        'rawData/F07/VCV/Day02/GAMBOALÓPEZ~ S_a8df7304-f513-4268-bb9b-5cf7a3676dad.edf',
        'rawData/F08/VCV/Day02/BOJEESTEVEZ~ M_3d3c60c8-979a-4142-8cef-e1d23157d309.edf',
        'rawData/F09/VCV/Day01/JIMÉNEZÁLVAREZ_5faa5598-a375-40c1-8840-b9ad8ae49a0a.edf',
        'rawData/F09/VCV/Day02/JIMÉNEZÁLVAREZ_d4e0ac36-a214-47cf-b0f3-ed4b8048c519.edf',
        'rawData/F10/VCV/GOMEZCARMONA~ _67e7880a-4065-4e37-a165-58982f5f8c3c.edf',
        'rawData/M06/VCV/Day01/MOLINARESSOSA~_2efaa8cf-328b-4bd2-8a30-173b125e1935.edf',
        'rawData/M06/VCV/Day01/MOLINARESSOSA~_2efaa8cf-328b-4bd2-8a30-173b125e1935.edf',
        'rawData/M06/VCV/Day02/MOLINARESSOSA~_eabeeee0-1eeb-40b1-8d22-fe3d3eb23800.edf',
        'rawData/M11/VCV/Day01/PIEDRAHITAGOME_7633df8c-5836-4d66-99c6-55b1cbb0951b.edf',
        'rawData/M12/VCV/Day02/COLLADOEXPOSIT_37f5a1d5-5756-4494-87d0-8f23b372c806.edf'    
    ]
    
    xdfPaths = [
        'rawData/F01/VCV/sub-VanesaRaelArribas_ses-Ses01_task-Default_run-001_eeg.xdf',
        'rawData/F01/VCV/sub-VanesaRaelArribas_ses-Ses02_task-Default_run-001_eeg.xdf',
        'rawData/F05/VCV/Day01/sub-Edita_ses-S001_task-Default_run-001_eeg.xdf',
        'rawData/F05/VCV/Day01/sub-Edita_ses-S002_task-Default_run-001_eeg.xdf',
        'rawData/F05/VCV/Day02/sub-Edita_ses-S005_task-Default_run-001_eeg.xdf',
        'rawData/F07/VCV/Day01/sub-SoniaGamboaLopez_ses-VCV_Ses01_task-Default_run-001_eeg.xdf',
        'rawData/F07/VCV/Day02/sub-SoniaGamboaLopez_ses-VCV_Ses02_task-Default_run-001_eeg.xdf',
        'rawData/F08/VCV/Day02/sub-MaCarmenBoje_ses-VCV_Ses02_task-Default_run-001_eeg.xdf',
        'rawData/F09/VCV/Day01/sub-AntoniaJimenezAlvarez_ses-VCV_Ses01_task-Default_run-001_eeg.xdf',
        'rawData/F09/VCV/Day02/sub-AntoniaJimenezAlvarez_ses-VCV_Ses02_task-Default_run-001_eeg.xdf',
        'rawData/F10/VCV/sub-MartaGomezCarmona_ses-VCV_Ses01_task-Default_run-001_eeg.xdf',
        'rawData/M06/VCV/Day01/sub-EduardoMolinares_ses-Ses01_task-Default_run-001_eeg.xdf',
        'rawData/M06/VCV/Day01/sub-EduardoMolinares_ses-Ses02_task-Default_run-001_eeg.xdf',
        'rawData/M06/VCV/Day02/sub-EduardoMolinares_ses-Ses03_task-Default_run-001_eeg.xdf',
        'rawData/M11/VCV/Day01/sub-EmilioPiedrahitaGomez_ses-VCV01_task-Default_run-001_eeg.xdf',
        'rawData/M12/VCV/Day02/sub-ColladoExposito_ses-VCV_02_task-Default_run-001_eeg.xdf'
    ]


    for index in range(len(subjectIDs)):
        index = 7
        subjectId = subjectIDs[index]
        sessionId = sessionIDs[index]
        filepathEeg = edfPaths[index]
        filepathAudio = xdfPaths[index]
        taskName = 'VCV'
        print(f'Subject ID| {subjectId} Session Id:  {sessionId}, {xdfPaths[index]}, {edfPaths[index]}')
        
        eegData = EegDataProcessor(filepathEeg)
        audioData = AudioDataProcessor(filepathAudio)

        eegAudioData = EegAudioDataProcessor(
            eegData=eegData, 
            audioData=audioData,
            taskName=taskName,
            subjectID=subjectId,
            sessionID=sessionId,
            runID='01' 
        ) 
        
        break
        
    if config.analyseAudio:

        folder = 'BIDS/sub-06/ses-03/audio'
        subjectId = folder.split('/')[1]
        sessionId = folder.split('/')[2]
        audioAnalyser = AudioAnalyser(folder, subjectId=subjectId, sessionId=sessionId)
