from utils import *

filename = 'current_il_data.txt'
data = read_spice_data(filename)
json_filename = 'datasheet_and_constants.json'
const = read_json_data(json_filename)

ton_sim = const["circuit"]["ton_sim"]
R2 = const["circuit"]["R2"]
L = const["circuit"]["L"]
ia = const["circuit"]["ia"]
ib = const["circuit"]["ib"]
V2 = const["circuit"]["V2"]
VD = const["circuit"]["VD"]


t_left = 40*1e-6
t_right = 0e-6

# ltspice no tiene intervalos de tiempo uniforme asi que tengo que buscar los indices para +/- un tiempo
start,l, r = get_synchronization_data(data['time'],data['V(gg)'], t_left, t_right)

time = data['time']

time_plot = data['time'][l:r]
vgg_plot = data['V(gg)'][l:r]    
iL_plot = data['I(L1)'][l:r]   


visual_time_shift = time_plot[0] 
shifted_time = time_plot-visual_time_shift

plt.plot(shifted_time,iL_plot, label='iL (sim)')

time_il_curves = np.linspace(0, ton_sim, num=100)
il_curve_1 = (V2/R2) + ia*np.exp(-(R2/L)*(time_il_curves))
il_curve_2= -(VD/R2) + ib*np.exp(-(R2/L)*time_il_curves)


il_teo = np.hstack((il_curve_1,il_curve_2,il_curve_1,il_curve_2))
time_teo = np.linspace(0, 4*ton_sim, num=400)


plt.plot(time_teo,il_teo, label='iL (teo)')


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