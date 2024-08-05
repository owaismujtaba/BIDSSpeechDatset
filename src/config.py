import os
from pathlib import Path

currDir = os.getcwd()
bidsDir = Path(currDir, 'BIDS')
numWorkers = 20

bidsEventsHeader = [
    'onset', 'duration', 'eegOnsetIndex', 
    'audioOnset', 'audioDuration', 'audioOnsetIndex',
    'eegOnsetUnixTime', 'audioOnsetUnixTime',
    'block', 'trialType', 'word'
]
