import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import json
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from matplotlib.ticker import EngFormatter


def get_last_pos_edge_idx(x, time, peak_height = 2, plot_peaks=False):
    peaks, _ = find_peaks(x, height=peak_height)
    if(plot_peaks):
        plt.plot(time, x)
        plt.plot(time[peaks], x[peaks], "x")
    return peaks[-1]

def get_right_index_till_time(time, center_idx, t_sw):
    curr_time_idx = center_idx
    while(time[curr_time_idx]-time[center_idx] <= t_sw):
        curr_time_idx += 1
    return curr_time_idx

def get_left_index_till_time(time, center_idx, t_sw):
    curr_time_idx = center_idx
    while(time[center_idx] - time[curr_time_idx] <= t_sw):
        curr_time_idx -= 1
    return curr_time_idx

def get_synchronization_data(time, sync_signal, t_left, t_right):
    either_edges = np.diff(sync_signal)
    center_idx = get_last_pos_edge_idx(either_edges,time=time[:-1], plot_peaks=False)
    left_idx = get_left_index_till_time(time, center_idx, t_left)
    right_idx = get_right_index_till_time(time, center_idx, t_right)
    return center_idx, left_idx, right_idx

def plot_point(index, time, signal, color):
    x = time[index]
    y = signal[index]
    plt.plot([x], [y], 'o', color=color, ms=4)
    plt.text(x, y, "{:0.2f}".format(x*1e9), size = 7)

def read_spice_data(filename):
    data_info = pd.read_csv(filename, sep ='\t', header = 0)
    data = {}
    for col in data_info.columns:
        data[col] = np.array(data_info[col].tolist())
    return data

def read_json_data(json_filename):
    const = None
    with open(json_filename, 'r') as myfile:
        const =json.loads(myfile.read()) 
    return const

    