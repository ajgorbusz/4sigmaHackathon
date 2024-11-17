import mne
import numpy as np
from scipy.signal import find_peaks, detrend
import matplotlib.pyplot as plt
import chess
import chess.engine

# This code contains core features with test data, no real time processing

BLINK_DIST = 1.8

LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
NUMBERS = [1,2,3,4,5,6,7,8]

TEST_MOVES_FILES = ['f3f3.fif', 'f2f3.fif', 'g2g4.fif']
it = 0

# Method to find blinks event (this method is for playtest)
def find_blinks(filename, channel):
    # Loading data from .fif file
    raw = mne.io.read_raw_fif(filename, preload=True)

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

    # Calculating dynamic threshold for peaks
    mean_amplitude = np.mean(np.abs(data))  #average value (absolute value)
    data = -data # Reversing data to convert valleys to peaks
    threshold = 0.8*mean_amplitude # dynamic threshold: 0.8*average value

    # Detecting events with high amplitudes
    peaks, _ = find_peaks(data, distance=fs * 0.5, height=threshold)  # Minimum distance between two events: 0.5 seconds (average time for a blink)

    # Analyzing only times of the events
    peak_times = times[peaks]

    # Displaying values
    plt.figure(figsize=(12, 6))
    plt.plot(times, data, label="EEG Signal")
    plt.plot(times[peaks], data[peaks], 'r^', label="Detected Blinks")
    plt.axhline(threshold, color='g', linestyle='--', label="Threshold")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (µV)")
    plt.legend()
    plt.title(f"Detected Blinks in {channel} Channel with Dynamic Threshold")
    plt.show()

    return peak_times

# Detecting yes or no (playtest)
def confirm(filename, channel='O1'):
    peaks = find_blinks(filename, channel)
    if len(peaks) == 1:
        return True
    
    else:
        return False

# Method to convert blinks to chess move
def makeMove(filename, channel='O1'):
    times = find_blinks(filename, channel)
    n = len(times)

    times1 = []
    times2 = []
    times3 = []
    times4 = []

    sep = []

    for i in range(1,n):
        if times[i] - times[i-1] > BLINK_DIST:
            sep.append(i)

    times1 = times[0:sep[0]]
    times2 = times[sep[0]:sep[1]]
    times3 = times[sep[1]:sep[2]]
    times4 = times[sep[2]:]

    lengths = [len(times1), len(times2), len(times3), len(times4)]
    for i in range(0,4):
        if lengths[i] > 8:
            lengths[i] = 8

    move = LETTERS[lengths[0]-1] + str(NUMBERS[lengths[1]-1]) + LETTERS[lengths[2]-1] + str(NUMBERS[lengths[3]-1])
    return move.lower()

# Stockfish path
STOCKFISH_PATH = 'stockfish/stockfish-ubuntu-x86-64-sse41-popcnt'  # Zmień na swoją ścieżkę!

# Players move (simulate only)
def player_move(board):
    while True:
        try:
            move_invalid = True
            while move_invalid:
                print("Your move: ")
                # This is for simulating playing only
                global it
                move = makeMove(TEST_MOVES_FILES[it])
                print(move)
                it += 1
                print('Do you want to perform this move?')
                if confirm('yes.fif'): #Simulating possitive answer
                    move_invalid = False
            if chess.Move.from_uci(move) in board.legal_moves:
                return move
            else:
                print("Illegal move, try again.")
        except ValueError:
            print("Wrong move format")

# Stockfishes move
def stockfish_move(board, engine):
    # Chess engine settings
    result = engine.play(board, chess.engine.Limit(time=1.0))
    return result.move

# Main game
def play_game():
    board = chess.Board()

    # Stockfish initialize
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        while not board.is_game_over():
            print(board)

            if board.turn:  # Players move
                move = player_move(board)
            else:  # Stockfishes move
                move = stockfish_move(board, engine)
                print(f"Stockfish plays: {move}")

            # Making move
            board.push_uci(str(move))

        print(board)
        print("Game over!")
        print("Result:", board.result())

# Uruchomienie gry
if __name__ == '__main__':
    play_game()