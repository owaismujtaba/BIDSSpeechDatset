import mne


def loadEdfFile(filepath):
    print(f'*******************Loading {filepath} File*******************')
    raw = mne.io.read_raw_edf(filepath, preload=True)
    print(f'*******************Loaded {filepath} File*******************')

    return raw