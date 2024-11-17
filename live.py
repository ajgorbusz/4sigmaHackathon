import brainaccess_board as bb
import mne
import time
from scipy.signal import find_peaks, detrend

# This code contains test version of live detection of input from user

# Getting data from database
def get_data():
    db, status = bb.db_connect()
    if status:
        data = db.get_mne()
        timestamp = data[next(iter(data))].times[-1]
        mne_struct = data[next(iter(data))]
        mne_struct.save('test_file.fif', overwrite=True)
        return timestamp
    
# Method to find and count blinks event
def find_blinks(filename, channel, timestamp1, timestamp2=None):
    # Loading data from .fif file
    raw = mne.io.read_raw_fif(filename, preload=True)
    raw.crop(timestamp1, timestamp2)

    # Picking channel to analyze
    raw.pick_channels([channel])

    # Filtring signal
    raw.filter(l_freq=None, h_freq=5.0, method='iir')

    # Getting data and times from .fif file
    data, times = raw.get_data(return_times=True)
    data = data.flatten()  #flattening the plot
    fs = raw.info['sfreq']

    # Detrending data
    data = detrend(data)

    # Detecting events with high amplitudes
    peaks, _ = find_peaks(data, distance=fs * 0.5, height=0.0001)  # Minimum distance between two events: 0.5 seconds (average time for a blink)

    # Analyzing only times of the events
    peak_times = times[peaks]

    return peak_times

LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
NUMBERS = ['1','2','3','4','5','6','7','8']

move = ''

print('Starting')
time.sleep(2)
blinking = True
timestamp1 = get_data()
ts1 = timestamp1
print('Start')
while blinking:
    time.sleep(0.1)
    n = len(find_blinks('test_file.fif', 'O1', timestamp1))
    if n > 0:
        timestamp1 = get_data()
    
    timestamp2 = get_data()
    if timestamp2 - timestamp1 > 2:
        blinking = False

move += LETTERS[len(find_blinks('test_file.fif', 'O1', ts1, timestamp2))]

blinking = True
timestamp1 = get_data()
ts1 = timestamp1
print('Start')
while blinking:
    time.sleep(0.1)
    n = len(find_blinks('test_file.fif', 'O1', timestamp1))
    if n == 1:
        timestamp1 = get_data()
    
    timestamp2 = get_data()
    if timestamp2 - timestamp1 > 2:
        blinking = False

move += NUMBERS[len(find_blinks('test_file.fif', 'O1', ts1, timestamp2))]

blinking = True
timestamp1 = get_data()
ts1 = timestamp1
print('Start')
while blinking:
    time.sleep(0.1)
    n = len(find_blinks('test_file.fif', 'O1', timestamp1))
    if n > 0:
        timestamp1 = get_data()
    
    timestamp2 = get_data()
    if timestamp2 - timestamp1 > 2:
        blinking = False

move += LETTERS[len(find_blinks('test_file.fif', 'O1', ts1, timestamp2))]

blinking = True
timestamp1 = get_data()
ts1 = timestamp1
print('Start')
while blinking:
    time.sleep(0.1)
    n = len(find_blinks('test_file.fif', 'O1', timestamp1))
    if n == 1:
        timestamp1 = get_data()
    
    timestamp2 = get_data()
    if timestamp2 - timestamp1 > 2:
        blinking = False

move += NUMBERS[len(find_blinks('test_file.fif', 'O1', ts1, timestamp2))]

print(move)
