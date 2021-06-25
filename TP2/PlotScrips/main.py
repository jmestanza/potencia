from utils import read_spice_data, read_json_data
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
from matplotlib.ticker import AutoMinorLocator

if __name__ == '__main__':
    json_data = read_json_data('plot_info.json')
    plots = json_data['plots']
    for plot in plots:
        filename = plot['spice_filename']
        data_filename = 'resources/' + filename + '.txt'
        data = read_spice_data(data_filename)
        time = data[plot['spice_time_label']]

        plt.title(plot['title'])

        fig, ax1 = plt.subplots()
        fig.set_size_inches(tuple(json_data['fig_size']))

        # left y axis
        ax1.set_ylabel(plot['left_y_label'])
        ax1.set_xlabel(plot['x_label'])
        ax1.set_ylim(tuple(plot['left_y_limit']))
        plt.grid(which="major", alpha=json_data['major_tick_alpha'])
        plt.grid(which="minor", alpha=json_data['minor_tick_alpha'])

        formatter1 = EngFormatter(places=2, sep="\N{THIN SPACE}")  # U+2009
        plt.gca().xaxis.set_major_formatter(formatter1)
        plt.gca().xaxis.set_minor_locator(AutoMinorLocator())
        plt.gca().yaxis.set_minor_locator(AutoMinorLocator())

        ax1.set_xlim(tuple(plot['x_limit']))

        plt.grid(True)
        if not plot['is_one_direction']:
            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
            ax2.set_ylabel(plot['right_y_label'])  # we already handled the x-label with ax1
            ax2.set_ylim(tuple(plot['right_y_limit']))

        lines = []
        for graphic in plot['graphics']:
            curr_data = data[graphic['spice_label']]
            if 'belongsToRightYAxis' not in graphic or not graphic['belongsToRightYAxis']:
                lines.extend(ax1.plot(time, curr_data, **graphic['config']))
            else:
                lines.extend(ax2.plot(time, curr_data, **graphic['config']))

        plt.legend(lines, [line.get_label() for line in lines])
        plt.savefig('output/' + plot['title'])
