import mne
import pyxdf
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import src.config as config
import pdb

def findClosestStartingIndex(timeStamps, time):
    differences = np.abs(timeStamps - time)
    closestIndex = np.argmin(differences)
    return closestIndex

def findNearestIndex(audioTimestamps, marker):
    
    idx = np.searchsorted(audioTimestamps, marker, side="left")
    if idx == 0:
        return 0
    elif idx == len(audioTimestamps):
        return len(audioTimestamps) - 1
    else:
        if abs(audioTimestamps[idx] - marker) < abs(audioTimestamps[idx - 1] - marker):
            return idx
        else:
            return idx - 1

def findNearestIndices(audioTimestamps, markerTimestamps):
    audioTimestamps = np.sort(audioTimestamps)
    nearestIndices = []
    
    with ThreadPoolExecutor(max_workers=config.numWorkers) as executor:
        futures = [executor.submit(findNearestIndex, audioTimestamps, marker) for marker in markerTimestamps]
        for future in futures:
            nearestIndices.append(future.result())
    
    return nearestIndices

def triggerEncodings(code):
    """
    Converts trigger codes into their corresponding marker names based on a predefined dictionary.
    If the exact code is not found, the closest code is used.

    This function maps an integer trigger code to a human-readable marker name using a predefined 
    dictionary of codes and their corresponding marker names. If the exact code is not found in the 
    dictionary, the function finds and returns the marker name of the closest available code.

    Parameters:
    code (int): Trigger code to be converted.

    Returns:
        str: Corresponding marker name if the code is found in the dictionary. If the exact code is 
         not found, the marker name of the closest code is returned.

    Example:
    >>> TriggerEncodings(200)
    'StartSaying'

    >>> TriggerEncodings(10)
    'ExperimentEnded'
    """
    
    markerNames = {
        255: 'StartReading',
        224: 'ITI',#'EndReading',
        192: 'StartSaying',
        160: 'Fixation',#'EndSaying',
        128: 'StartBlockSaying',
        96: 'StartBlockThinking',
        64: 'EXPERIMENT_RESTART',
        32: 'ExperimentResting',
        16: 'ExperimentStarted',
        8: 'ExperimentEnded'
    }

    markerName = markerNames.get(code)
    
    if markerName:
        return markerName
    
    closestCode = min(markerNames.keys(), key=lambda k: abs(k - code))
    closestMarkerName = markerNames[closestCode]
    
    return closestMarkerName

def eegNormalizeTriggers(triggerValues):
    """
    Normalizes EEG trigger values to a range from 0 to 255.

    This function normalizes an array of EEG trigger values using the formula:
    normalizedValue = (triggerValue - triggerMin) / (triggerMax - triggerMin) * 255.
    The trigger values are first inverted (multiplied by -1) before normalization. The resulting 
    normalized values are rounded to the nearest integer.

    Parameters:
    triggerValues (np.ndarray): Array containing trigger values to be normalized.

    Returns:
    np.ndarray: Array of normalized trigger values rounded to the nearest integer.

    Example:
    >>> triggerValues = np.array([10, 20, 30, 40, 50])
    >>>
        >>> triggerValues = np.array([10, 20, 30, 40, 50])
    >>> NormalizeEegTriggers(triggerValues)
    array([255, 204, 153, 102,  51])
    """
    print(f'****************Normalizing Triggers********************')
    triggerValues = triggerValues * -1
    triggerMin = np.min(triggerValues)
    triggerMax = np.max(triggerValues)
    
    normalizedTriggers = (triggerValues - triggerMin) / (triggerMax - triggerMin) * 255
    normalizedTriggers = np.round(normalizedTriggers).astype(int)
    print('***************************Triggeres Normalized**********************')
    return normalizedTriggers

def eegCorrectTriggers(triggers):
    """
    Corrects a list of EEG triggers by mapping them to the nearest valid code
    from a predefined set of correct codes.

    This function takes a list of integer EEG trigger codes and corrects them by mapping 
    each trigger to the nearest valid code from a predefined set of valid codes. If a trigger 
    code is not in the predefined set, it is mapped to the closest valid code.

    Parameters:
    triggers (list of int): A list of integer trigger codes to be corrected.

    Returns:
    list of int: A list of corrected trigger codes. Each input trigger is either directly 
                 mapped if it exists in the valid codes, or mapped to the nearest valid code 
                 if it does not.

    Example:
    >>> triggers = [5, 20, 100, 130]
    >>> CorrectEegTriggers(triggers)
    [8, 16, 96, 128]
    """
    print(f'****************Correcting Triggers********************')
    correctCodings = {
        255: 255, 224: 224, 192: 192, 160: 160,
        128: 128, 96: 96, 64: 64, 32: 32, 16: 16, 8: 8
    }

    validCodes = sorted(correctCodings.keys())

    maxTrigger = max(validCodes)
    nearestCodeMap = {}

    for i in range(maxTrigger + 1):
        nearestCode = min(validCodes, key=lambda x: abs(x - i))
        nearestCodeMap[i] = correctCodings[nearestCode]

    correctedTriggers = []
    for trigger in triggers:
        if trigger in nearestCodeMap:
            correctedTriggers.append(nearestCodeMap[trigger])
        else:
            correctedTriggers.append(nearestCodeMap[maxTrigger])
            print('Trigger coding Error')
    
    return correctedTriggers

def eegTransitionTriggerPoints(triggerArray):
    """
    Identifies the transition points in an EEG trigger array.

    This function takes a 1D numpy array of EEG trigger values and identifies the indexes where
    transitions occur. A transition is defined as a change from a lower value to a higher value 
    between consecutive elements in the trigger array. The function returns an array of indexes 
    indicating the positions of these transition points.

    Parameters:
    triggerArray (np.ndarray): A 1D numpy array containing the trigger values from EEG data.

    Returns:
    np.ndarray: An array of indexes where transitions occur in the trigger array. The first 
                element of the returned array is always 0 to indicate the start of the array.
                
    Example:
    >>> triggerArray = np.array([0, 0, 1, 1, 0, 0, 1, 1, 0])
    >>> EegTransitionTriggerPoints(triggerArray)
    array([0, 2, 6])
    """
    print(f'**************** Calculating EEG Transition Indexes********************')
    differenceArray = np.where(np.diff(triggerArray) > 0)[0] + 1
    transitionPointsIndexes = np.array([0] + differenceArray.tolist())
    
    return transitionPointsIndexes

def loadEdfFile(filepath):
    print(f'*******************Loading {filepath} File*******************')
    raw = mne.io.read_raw_edf(filepath, preload=True, verbose=False)
    print(f'*******************Loaded {filepath} File*******************')

    return raw

def loadXdfFile(filepath):
    """
        Load data from an XDF (Extensible Data Format) file.

        Parameters:
        - filepath (str): The filepath to the XDF file.

        Returns:
        - streams (list): A list containing streams of data loaded from the XDF file using pyxdf library.
        - header (dict): A dictionary containing header information of the XDF file.

        Dependencies:
        - pyxdf: Python library for reading XDF files.
    """
    print('*********************************************************************************')
    print('***************************Loading .xdf file***************************')
    
    # Use pyxdf library to load data from the XDF file
    streams, header = pyxdf.load_xdf(filepath)
    print('*******************************Completed*******************************')

    return streams, header

def adjustAudioTime(unixTimestamps):
    if config.adjustTime:
        gap = 2
    else:   
        gap = 0
    gapUnix = gap * 3600
    return unixTimestamps + gapUnix