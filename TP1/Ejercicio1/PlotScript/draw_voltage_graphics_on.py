from utils import *
from constants import *

filename = 'voltages_sim_data.txt'
data = read_spice_data(filename)
json_filename = 'datasheet_and_constants.json'
const = read_json_data(json_filename)

Rg = const["circuit"]["Rg"]
VGG = const["circuit"]["VGG"]
io = const["circuit"]["io"]


VDSMAX = const["datasheet"]["VDSMAX"]
VGSIO = const["datasheet"]["VGSIO"]
Ciss_first = const["datasheet"]["Ciss_first"]
Ciss_second = const["datasheet"]["Ciss_second"]
Cgd1 = const["datasheet"]["Cgd1"]
Cgd2 = const["datasheet"]["Cgd2"]
deltaq = const["datasheet"]["deltaq"]
VGSTH = const["datasheet"]["VGSTH"]



Cgs = Ciss_first-Cgd1
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

tau_2 = Rg*Ciss_second

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

# Pongo los puntos en los puntos de interes.
plot_point(index=14, time=time_teo, signal=vgs_plot, color='orange')
plot_point(index=37, time=time_teo, signal=vgs_plot, color='orange') 
plot_point(index=65, time=time_teo, signal=vgs_plot, color='orange')
plot_point(index=114, time=time_teo, signal=vgs_plot, color='orange')

plt.grid()

formatter1 = EngFormatter(places=2, sep="\N{THIN SPACE}")  # U+2009
ax = plt.gca()
plt.gca().xaxis.set_major_formatter(formatter1)
plt.legend()
plt.show()