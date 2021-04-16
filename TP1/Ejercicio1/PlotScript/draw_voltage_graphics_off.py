from utils import *

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

tau_1 = Rg*Ciss_first

ig = VGSIO/Rg #chequeada ig con la simulacion

# lo unico que puede estar mal es el delta Q  <= falso
# implca que lo unico que puede estar mal es Vgsio, que esta en 5.3 o sea, falso
# lo cual implica que puede que este mal la corriente, falso

# todas estas suposiciones son malas...

t_rv = deltaq/ig 
print("t_rv= ",t_rv*1e9,"ns")


t_rv2 = VDSMAX/(ig/Cgd1)
print("t_rv2= ",t_rv2*1e9,"ns")


tau_2 = Rg*Ciss_second

t_left = 0.1e-9
# t_right = 400e-9
t_right = 415e-9

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
vgg_curve_0 = VGG * np.ones((end_curve_0-l))

td_off = -tau_2*np.log(VGSIO/VGG)
print("td_off", td_off*1e9, "ns")

end_curve_1 = get_right_index_till_time(time, end_curve_0, td_off)
vgg_curve_1 = VGG*(np.exp(-(time[end_curve_0:end_curve_1] - time[end_curve_0])/tau_2))

end_curve_2 = get_right_index_till_time(time, end_curve_1, t_rv)
vgg_curve_2 = np.ones((end_curve_2-end_curve_1))*VGSIO

end_curve_3 = get_right_index_till_time(time, end_curve_2, 2*tau_1)
vgg_curve_3 = VGSIO*(np.exp(-(time[end_curve_2: end_curve_3]- time[end_curve_2])/tau_1))

vgg_teo = np.hstack((vgg_curve_0,vgg_curve_1,vgg_curve_2,vgg_curve_3))
time_teo = shifted_time[:len(vgg_teo)]

plt.plot(time_teo,vgg_teo, label='Vgs (teo)')

plot_point(index=50, time=time_teo, signal=vgs_plot, color='orange')
plot_point(index=114, time=time_teo, signal=vgs_plot, color='orange')
plot_point(index=141, time=time_teo, signal=vgs_plot, color='orange')

formatter1 = EngFormatter(places=2, sep="\N{THIN SPACE}")  # U+2009
ax = plt.gca()
plt.gca().xaxis.set_major_formatter(formatter1)
plt.gca().xaxis.set_minor_locator(AutoMinorLocator())
plt.gca().yaxis.set_minor_locator(AutoMinorLocator())
plt.grid(which="major",alpha=0.8)
plt.grid(which="minor",alpha=0.3)

plt.ylabel('tensión (V)')
plt.xlabel('tiempo (s)')


plt.legend()
plt.show()