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

filename = 'voltages_on.txt'

data_info = pd.read_csv(filename, sep ='\t', header = 0)
data = {}
for col in data_info.columns:
    data[col] = np.array(data_info[col].tolist())
    
Rg = 100 # con Rg = 115, daba bastante bien... debe ser que cambia la R pero no se porque
VDSMAX = 13
VGSIO = 5.4
VGG = 12
VGSTH = 4 
Ciss_first = 700e-12
deltaq = 5.5e-9
Cgd1 = 70e-12
Cgs = Ciss_first-Cgd1

Cgd2 = 500e-12

tau_1 = Rg*Ciss_first

ig = VGSIO/Rg #chequeada ig con la simulacion

# lo unico que puede estar mal es el delta Q  <= falso
# implca que lo unico que puede estar mal es Vgsio, que esta en 5.3 o sea, falso
# lo cual implica que puede que este mal la corriente, falso

# todas estas suposiciones son malas...

t_rv = deltaq/ig 
print("t_rv= ",t_rv*1e9,"ns")

Ciss_second = 1140e-12
# otra forma es Rg*(Cgd2+Cgs)
tau_2 = Rg*Ciss_second
print(tau_2*1e9)
tau_2 = Rg*(Cgd2+Cgs)
print(tau_2*1e9)

t_left = 0.1e-9
t_right = 0.8e-6

# ltspice no tiene intervalos de tiempo uniforme asi que tengo que buscar los indices para +/- un tiempo
start,l, r = get_synchronization_data(data['time'],-data['V(gg)'], t_left, t_right)

time = data['time']

time_plot = data['time'][l:r]
vgg_plot = data['V(gg)'][l:r]    
vgs_plot = data['V(g)'][l:r]   
vds_plot = data['V(d)'][l:r]   

visual_time_shift = time_plot[0]
shifted_time = time_plot-visual_time_shift

plt.plot(shifted_time,vgg_plot, label='Vgg (sim)')
plt.plot(shifted_time,vgs_plot, label='Vgs (sim)')
plt.plot(shifted_time,vds_plot, label='Vds (sim)')

end_curve_0 = start
vgg_curve_0 = np.zeros((end_curve_0-l))

td_off = -tau_2*np.log(VGSIO/VGG)

end_curve_1 = get_right_index_till_time(time, end_curve_0, td_off)
vgg_curve_1 = VGG*(np.exp(-(time[end_curve_0:end_curve_1] - time[end_curve_0])/tau_2))

end_curve_2 = get_right_index_till_time(time, end_curve_1, t_rv)
vgg_curve_2 = np.ones((end_curve_2-end_curve_1))*VGSIO

init_time = 60e-9 # lo ajuste a mano, era mas facil q calcularlo
end_curve_3 = get_right_index_till_time(time, end_curve_2, 3*tau_2)
vgg_curve_3 = VGG*(np.exp(-(time[end_curve_2: end_curve_3]- time[end_curve_2] + init_time)/tau_1))

vgg_curve = np.hstack((vgg_curve_0,vgg_curve_1))
vgg_curve = np.hstack((vgg_curve,vgg_curve_2))
vgg_curve = np.hstack((vgg_curve,vgg_curve_3))

time_teo = shifted_time[:len(vgg_curve)]
vgg_teo = vgg_curve
plt.plot(time_teo,vgg_teo, label='Vgs (teo)')


plot_point(index=50, time=time_teo, signal=vgs_plot, color='orange') # este hay que ver corriente
plot_point(index=114, time=time_teo, signal=vgs_plot, color='orange')
plot_point(index=141, time=time_teo, signal=vgs_plot, color='orange')

plt.grid()

formatter1 = EngFormatter(places=2, sep="\N{THIN SPACE}")  # U+2009
ax = plt.gca()
plt.gca().xaxis.set_major_formatter(formatter1)
# plt.grid(which='both')
plt.legend()
plt.show()