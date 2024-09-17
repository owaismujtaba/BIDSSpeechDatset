import os
from pathlib import Path

currDir = os.getcwd()
bidsDir = Path(currDir, 'BIDS_1')
numWorkers = 20

use_gui = True
windowIconPath = ''
audioPlayerDir = Path(currDir, 'SampleAudios')
bidsEventsHeader = [
    'onset', 'duration', 'eegOnsetIndex', 
    'audioOnset', 'audioDuration', 'audioOnsetIndex',
    'eegOnsetUnixTime', 'audioOnsetUnixTime',
    'block', 'trialType', 'word'
]
timeDifference = 0
removeChannel147 = True
analyseAudio = False
os.makedirs(bidsDir, exist_ok=True)
