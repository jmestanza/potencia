from utils import *

filename = 'currents_sim_data.txt'
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

plt.plot(shifted_time,id_plot, label='IDrain (sim)')
plt.plot(shifted_time,iL_plot, label='IL (sim)')
plt.plot(shifted_time,iD1_plot, label='Idiodo (sim)')

print('td_on_plus_t_ri (ns)=', td_on_plus_t_ri*1e9)


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



id_teo = np.hstack((id_curve_0,id_curve_1,id_curve_2,id_curve_3))
time_teo = shifted_time[:len(id_teo)]


plt.plot(time_teo,id_teo, label='id (teo)')

print(np.searchsorted(id_plot, td_on))
# Pongo los puntos en los puntos de interes.
plot_point(index=14, time=time_teo, signal=id_plot, color='blue') 
plot_point(index=37, time=time_teo, signal=id_plot, color='blue')
plot_point(index=65, time=time_teo, signal=id_plot, color='blue')

plt.grid()

formatter1 = EngFormatter(places=2, sep="\N{THIN SPACE}")
ax = plt.gca()
plt.gca().xaxis.set_major_formatter(formatter1)
plt.legend()
plt.show()