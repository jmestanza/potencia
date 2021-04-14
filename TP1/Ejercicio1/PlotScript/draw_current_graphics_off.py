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

tau_1 = Rg*Ciss_first

ig = VGSIO/Rg #chequeada ig con la simulacion

# lo unico que puede estar mal es el delta Q  <= falso
# implca que lo unico que puede estar mal es Vgsio, que esta en 5.3 o sea, falso
# lo cual implica que puede que este mal la corriente, falso

# todas estas suposiciones son malas...
# Vgp es la plateau voltage => VGG creo...
#t_rv = deltaq/ig # RgCgd * Vds/Vgp
# i = dq/dt => q es c v
# q = cgd * vdsmax 
# t_rv = (Cgd1 * VDSMAX)/ig
# deltaq = 7.5e-9
t_rv = deltaq/ig

print("Nueva Rg=>", VGSIO/ig)

print("t_rv= ",t_rv*1e9,"ns")

# otra forma es Rg*(Cgd2+Cgs)
tau_2 = Rg*Ciss_second
print(tau_2*1e9)

td_off = -tau_2*np.log(VGSIO/VGG)

t_left = 0.1e-9
t_right = 500e-9

# ltspice no tiene intervalos de tiempo uniforme asi que tengo que buscar los indices para +/- un tiempo
start,l, r = get_synchronization_data(data['time'],-data['V(gg)'], t_left, t_right)

time = data['time']

time_plot = data['time'][l:r]
vgg_plot = data['V(gg)'][l:r]    
id_plot = data['Id(M1)'][l:r]   
iL_plot = data['I(L1)'][l:r]   
iD1_plot = data['I(D1)'][l:r]   

visual_time_shift = time_plot[0]
shifted_time = time_plot-visual_time_shift

plt.plot(shifted_time,id_plot, label='IDrain (sim)')
plt.plot(shifted_time,iL_plot, label='IL (sim)')
plt.plot(shifted_time,iD1_plot, label='Idiodo (sim)')

end_curve_0 = start
id_curve_0 = io*np.ones((end_curve_0-l))

end_curve_1 = get_right_index_till_time(time, end_curve_0, td_off+ t_rv)
id_curve_1 = io*np.ones((end_curve_1-end_curve_0))

# y(t) = VGSIO * e-(t/tau_1)
# cuando y(t_fi) = VGSTH
# -tau_1*ln(VGSTH/VGSIO)  = t_fi
t_fi = -tau_1*np.log(VGSTH/VGSIO) 
print("t_fi = ", t_fi*1e9 , "ns")

end_curve_2 = get_right_index_till_time(time, end_curve_1,  t_fi)
delta_y = io
delta_x = time[end_curve_2]-time[end_curve_1]
m = -delta_y/delta_x 
id_curve_2 = m*(time[end_curve_1:end_curve_2]-time[end_curve_1]) + io

end_curve_3 = get_right_index_till_time(time, end_curve_2, 50e-9)
id_curve_3 = np.zeros((end_curve_3-end_curve_2))

id_teo = np.hstack((id_curve_0,id_curve_1,id_curve_2,id_curve_3))
time_teo = shifted_time[:len(id_teo)]


plt.plot(time_teo,id_teo, label='Idrain (teo)')
# plt.plot(shifted_time,vgg_plot, label='Idrain (teo)')

# plt.arrow(0, 1, td_off, 0, head_width=0.04, head_length=td_off/10, linewidth=1, color='black', length_includes_head=True)
# plt.annotate('', xy=(0,1), xytext=(td_off,1), xycoords='axes fraction', arrowprops=dict(arrowstyle='<->'))
# plt.annotate('hola', xy=(0,1), xytext=(0,1), xycoords='data', arrowprops=dict(arrowstyle='<->'), annotation_clip = None)

plot_point(index=50, time=shifted_time, signal=id_plot, color='blue') 
plot_point(index=114, time=shifted_time, signal=id_plot, color='blue')
plot_point(index=141, time=shifted_time, signal=id_plot, color='blue')


formatter1 = EngFormatter(places=2, sep="\N{THIN SPACE}")  # U+2009
ax = plt.gca()
plt.gca().xaxis.set_major_formatter(formatter1)
plt.gca().xaxis.set_minor_locator(AutoMinorLocator())
plt.gca().yaxis.set_minor_locator(AutoMinorLocator())
plt.grid(which="major",alpha=0.8)
plt.grid(which="minor",alpha=0.3)

plt.ylabel('corriente (A)')
plt.xlabel('tiempo (s)')


plt.legend()
plt.show()