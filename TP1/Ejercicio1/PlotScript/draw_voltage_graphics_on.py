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
    
Rg = 100
VDSMAX = 13
VGSIO = 5.4
VGG = 12
VGSTH = 3 
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

# t_left = 0.005e-6
# t_left = 0.4e-9
# t_left = 0.3e-9
# t_left = 0.2e-9
t_left = 0.1e-9
t_right = 0.5e-6

# ltspice no tiene intervalos de tiempo uniforme asi que tengo que buscar los indices para +/- un tiempo

start,l, r = get_synchronization_data(data['time'],data['V(gg)'], t_left, t_right)

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
# ax2 = plt.gca().twinx()
# ax2.plot(time_plot,id_plot,'--', label='Id (sim)', color='red',)

end_curve_0 = start
vgg_curve_0 = np.zeros((end_curve_0-l))



print('td_on_plus_t_ri (ns)=', td_on_plus_t_ri*1e9)


end_curve_1 = get_right_index_till_time(time, end_curve_0, td_on_plus_t_ri)
vgg_curve_1 = VGG*(1-np.exp(-(time[end_curve_0:end_curve_1] - time[end_curve_0])/tau_1))

end_curve_2 = get_right_index_till_time(time, end_curve_1, t_fv)
vgg_curve_2 = np.ones((end_curve_2-end_curve_1))*VGSIO
print(end_curve_2)
end_curve_3 = get_right_index_till_time(time, end_curve_2, 3*tau_2)
print(end_curve_3)

init_time = -tau_2*np.log(1-VGSIO/VGG)
vgg_curve_3 = VGG*(1-np.exp(-(time[end_curve_2: end_curve_3]- time[end_curve_2] + init_time)/tau_2))
print(len(time[end_curve_3:end_curve_2]))

vgg_curve = np.hstack((vgg_curve_0,vgg_curve_1))
vgg_curve = np.hstack((vgg_curve,vgg_curve_2))
vgg_curve = np.hstack((vgg_curve,vgg_curve_3))

time_teo = shifted_time[:len(vgg_curve)]
vgg_teo = vgg_curve
plt.plot(time_teo,vgg_teo, label='Vgs (teo)')


plot_point(index=14, time=time_teo, signal=vgs_plot, color='orange') # este hay que ver corriente
plot_point(index=37, time=time_teo, signal=vgs_plot, color='orange') # este hay que ver corriente
plot_point(index=65, time=time_teo, signal=vgs_plot, color='orange')
plot_point(index=114, time=time_teo, signal=vgs_plot, color='orange')

plt.grid()

formatter1 = EngFormatter(places=2, sep="\N{THIN SPACE}")  # U+2009
ax = plt.gca()
plt.gca().xaxis.set_major_formatter(formatter1)
# plt.grid(which='both')
plt.legend()
plt.show()