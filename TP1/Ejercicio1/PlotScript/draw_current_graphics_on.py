import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

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
    plt.plot([x], [y], 'o', color=color, ms=6)
    plt.text(x, y, "{:0.2f}ns".format(x*1e9))

filename = 'currents_on.txt'

data_info = pd.read_csv(filename, sep ='\t', header = 0)
data = {}
for col in data_info.columns:
    data[col] = np.array(data_info[col].tolist())
    
Rg = 100
VDSMAX = 13
VGSIO = 5.4
VGG = 12
VGSTH = 4 # esto puede que cambie... elegi el promedio, pero en realidad deberia pedir 4, que es lo que se que funciona bajo cualquier cosa
Ciss_first = 700e-12
deltaq = 5.5e-9
Cgd1 = 70e-12
Cgs = Ciss_first-Cgd1

Cgd2 = 500e-12

tau_1 = Rg*Ciss_first

td_on = -tau_1*np.log(1-VGSTH/VGG)
print("td_on= ",td_on*1e9,"ns")
td_on_plus_t_ri = -tau_1*np.log(1-VGSIO/VGG)
t_ri = td_on_plus_t_ri - td_on
print("t_ri= ",t_ri*1e9,"ns")

ig = (VGG-VGSIO)/Rg
t_fv = deltaq/ig 
print("t_fv= ",t_fv*1e9,"ns")


t_fv1 = VDSMAX*(Rg*Cgd1)/(VGG-VGSIO)

print("t_fv1= ",t_fv1*1e9,"ns")


Ciss_second = 1140e-12
# tau_2 = Rg*(Cgd2+Cgs)
tau_2 = Rg*Ciss_second


t_left = 0.1e-9
# t_right = 200e-9
# t_right = 150e-9
t_right = 100e-9

# ltspice no tiene intervalos de tiempo uniforme asi que tengo que buscar los indices para +/- un tiempo

start,l, r = get_synchronization_data(data['time'],data['V(gg)'], t_left, t_right)

time = data['time']

time_plot = data['time'][l:r]
vgg_plot = data['V(gg)'][l:r]    
id_plot = data['Id(M1)'][l:r]   
iL_plot = data['I(L1)'][l:r]   
iD1_plot = data['I(D1)'][l:r]   


visual_time_shift = time_plot[0] # hay que ver que poner aca, 480e-6
shifted_time = time_plot-visual_time_shift

# plt.plot(shifted_time,vgg_plot, label='Vgg (sim)')
plt.plot(shifted_time,id_plot, label='IDrain (sim)')
plt.plot(shifted_time,iL_plot, label='IL (sim)')
plt.plot(shifted_time,iD1_plot, label='Idiodo (sim)')



print('td_on_plus_t_ri (ns)=', td_on_plus_t_ri*1e9)

io = 5.345

end_curve_0 = start
id_curve_0 = np.zeros((end_curve_0-l))

end_curve_1 = get_right_index_till_time(time, end_curve_0, td_on)
id_curve_1 = np.zeros((end_curve_1-end_curve_0))

end_curve_2 = get_right_index_till_time(time, end_curve_1, t_ri)
delta_y = io
delta_x = time[end_curve_2]-time[end_curve_1]
m = delta_y/delta_x
id_curve_2 = m*(time[end_curve_1:end_curve_2]-time[end_curve_1])

end_curve_3 = get_right_index_till_time(time, end_curve_2, 50e-9)
id_curve_3 = io*np.ones((end_curve_3-end_curve_2))


id_curve = np.hstack((id_curve_0,id_curve_1))
id_curve = np.hstack((id_curve,id_curve_2))
id_curve = np.hstack((id_curve,id_curve_3))

time_teo = shifted_time[:len(id_curve)]
id_teo = id_curve
plt.plot(time_teo,id_teo, label='id (teo)')


plot_point(index=14, time=time_teo, signal=id_plot, color='blue') # este hay que ver corriente
plot_point(index=37, time=time_teo, signal=id_plot, color='blue') # este hay que ver corriente
plot_point(index=65, time=time_teo, signal=id_plot, color='blue')

plt.grid()

formatter1 = EngFormatter(places=2, sep="\N{THIN SPACE}")  # U+2009
ax = plt.gca()
plt.gca().xaxis.set_major_formatter(formatter1)
plt.legend()
plt.show()