import os
from pathlib import Path

currDir = os.getcwd()
bidsDir = Path(currDir, 'BIDS')
numWorkers = 20

bidsEventsHeader = [
    'onset', 'duration', 'trial_type', 'block', 'audioOnset',
    'audioDuration', 'audioOnsetIndex', 'eegOnsetIndex', 'word'
]

